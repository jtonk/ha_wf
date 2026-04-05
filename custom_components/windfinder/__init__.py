"""Windfinder integration."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from numbers import Number
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
import voluptuous as vol

import json
import html as html_lib
import re
from bs4 import BeautifulSoup


from .const import (
    CONF_LOCATION,
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
    FORECAST_URL,
    MONTHS,
    PLATFORMS,
    SUPERFORECAST_URL,
)

_LOGGER = logging.getLogger(__name__)

MPS_TO_KNOTS = 1.9438444924406048

SERVICE_REFRESH = "refresh"
SERVICE_REFRESH_SCHEMA = vol.Schema({vol.Required(ATTR_ENTITY_ID): cv.entity_ids})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Windfinder component."""

    async def handle_refresh_service(call: ServiceCall) -> None:
        entity_ids = call.data[ATTR_ENTITY_ID]
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]
        registry = er.async_get(hass)
        for entity_id in entity_ids:
            entity_entry = registry.async_get(entity_id)
            coordinator = None
            if entity_entry:
                coordinator = hass.data.get(DOMAIN, {}).get(
                    entity_entry.config_entry_id
                )
            if coordinator:
                await coordinator.async_request_refresh()
            else:
                _LOGGER.warning("No Windfinder entity '%s' found", entity_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH,
        handle_refresh_service,
        schema=SERVICE_REFRESH_SCHEMA,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Windfinder from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = aiohttp_client.async_get_clientsession(hass)

    location = entry.options.get(CONF_LOCATION, entry.data[CONF_LOCATION])
    refresh_minutes = entry.options.get(CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL)
    coordinator = WindfinderDataUpdateCoordinator(
        hass,
        session=session,
        location=location,
        refresh_minutes=refresh_minutes,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class WindfinderDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Windfinder."""

    def __init__(self, hass, *, session, location, refresh_minutes: int):
        """Initialize coordinator."""
        interval = timedelta(minutes=refresh_minutes)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=interval)
        self._session = session
        self._location = location.lower()

    async def _async_update_data(self):
        """Fetch and parse data from Windfinder."""
        try:
            forecast_url = FORECAST_URL.format(self._location)
            superforecast_url = SUPERFORECAST_URL.format(self._location)

            async with self._session.get(forecast_url, timeout=10) as resp:
                resp.raise_for_status()
                forecast_html = await resp.text()

            async with self._session.get(superforecast_url, timeout=10) as resp:
                resp.raise_for_status()
                superforecast_html = await resp.text()

            # Use Home Assistant's configured time zone if available
            local_tz = (
                ZoneInfo(self.hass.config.time_zone)
                if self.hass.config.time_zone
                else timezone.utc
            )
            forecast = _parse_html(forecast_html, forecast_url, "forecast", local_tz)
            superforecast = _parse_html(
                superforecast_html,
                superforecast_url,
                "superforecast",
                local_tz,
            )

            result = {
                **forecast,
                **superforecast,
            }

            return result
        except Exception as err:
            raise UpdateFailed(err)


def _parse_html(
    html: str,
    url: str,
    forecast_type: str,
    local_tz: timezone = timezone.utc,
) -> dict:
    """Parse a Windfinder HTML table into structured data."""
    soup = BeautifulSoup(html, "html.parser")
    spot_meta = _astro_component_props(soup, "SpotMeta")
    spot_name = _spot_name_from_astro(spot_meta) or _first_text(
        soup,
        (
            "#spotheader-spotname",
            "[data-testid='spot-name']",
            ".spotheader-spotname",
            "h1.spot-name",
            ".spot-headline .large",
        ),
    )
    if not spot_name:
        spot_name = _spot_name_from_meta(soup)

    last_update, next_update = _parse_astro_update_info(
        soup,
        forecast_type,
        spot_meta,
        local_tz,
    )

    astro_forecasts = _parse_astro_forecast_data(soup, local_tz)
    astro_layout_forecasts = _parse_astro_layout_data(soup, local_tz)
    current_markup_forecasts = _parse_fc_day_rows(
        soup,
        local_tz,
        [
            item["datetime"]
            for item in astro_forecasts + astro_layout_forecasts
            if item.get("datetime")
        ],
    )

    forecasts = _combine_forecasts(
        astro_layout_forecasts,
        current_markup_forecasts,
        astro_forecasts,
    )

    # Bundle parsed results together with metadata
    return {
        forecast_type + "data": forecasts,
        forecast_type + "_fetched": datetime.now(timezone.utc).isoformat(),
        forecast_type + "_generated": last_update,
        forecast_type + "_last_update": last_update,
        forecast_type + "_next_update": next_update,
        "spot_name": spot_name,
        "spot_timezone": (
            spot_meta.get("spot", {}).get("o_id")
            if isinstance(spot_meta, dict)
            else None
        ),
    }


def _parse_headline_date(headline: str, now: datetime) -> date | None:
    """Extract a calendar date from a day headline.

    Windfinder currently renders multiple headline variants. Some include
    month names (e.g. "Sun, Apr 5"), while others only include day numbers
    for upcoming days in the same month.
    """
    clean = " ".join(headline.replace(",", " ").split())
    if not clean:
        return None

    today = now.date()
    lowered = clean.lower()
    if lowered.startswith("today"):
        return today
    if lowered.startswith("tomorrow"):
        return today + timedelta(days=1)

    iso_match = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", clean)
    if iso_match:
        try:
            return date(
                int(iso_match.group(1)),
                int(iso_match.group(2)),
                int(iso_match.group(3)),
            )
        except ValueError:
            return None

    month_aliases = {
        month.lower(): month_num for month, month_num in MONTHS.items()
    }
    month_aliases.update(
        {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }
    )

    month_day = re.search(
        r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:\b|st|nd|rd|th)",
        clean,
    )
    if month_day:
        month_name = month_day.group(1).lower()
        day_num = int(month_day.group(2))
        month = month_aliases.get(month_name)
        if month:
            year = now.year
            try:
                parsed = date(year, month, day_num)
            except ValueError:
                return None
            if parsed < today - timedelta(days=180):
                return date(year + 1, month, day_num)
            if parsed > today + timedelta(days=180):
                return date(year - 1, month, day_num)
            return parsed

    dotted = re.search(r"\b(\d{1,2})\.(\d{1,2})\.?\b", clean)
    if dotted:
        day_num = int(dotted.group(1))
        month = int(dotted.group(2))
        year = now.year
        try:
            parsed = date(year, month, day_num)
        except ValueError:
            return None
        if parsed < today - timedelta(days=180):
            return date(year + 1, month, day_num)
        if parsed > today + timedelta(days=180):
            return date(year - 1, month, day_num)
        return parsed

    day_only = re.search(r"\b(\d{1,2})(?:\b|st|nd|rd|th)", clean)
    if day_only:
        day_num = int(day_only.group(1))
        month = now.month
        year = now.year
        try:
            parsed = date(year, month, day_num)
        except ValueError:
            return None
        if parsed < today - timedelta(days=15):
            if month == 12:
                parsed = date(year + 1, 1, day_num)
            else:
                parsed = date(year, month + 1, day_num)
        return parsed

    return None


def _first_text(node, selectors: tuple[str, ...]) -> str | None:
    """Return the first non-empty text for the given CSS selectors."""
    for selector in selectors:
        element = node.select_one(selector)
        if not element:
            continue
        text = element.text.strip()
        if text:
            return text
    return None


def _spot_name_from_meta(soup: BeautifulSoup) -> str | None:
    """Extract the spot name from page metadata when headline selectors drift."""
    meta = soup.select_one("meta[property='og:title'], meta[name='twitter:title']")
    if not meta:
        return None

    content = (meta.get("content") or "").strip()
    if not content:
        return None

    for marker in (" forecast ", " Superforecast "):
        if marker in content:
            spot_name = content.split(marker, 1)[1].rsplit(" - Windfinder", 1)[0].strip()
            if spot_name:
                return spot_name

    return None


def _astro_component_props(soup: BeautifulSoup, component_name: str) -> dict | None:
    """Decode Astro component props for a named component fragment."""
    island = soup.select_one(f"astro-island[component-url*='{component_name}']")
    if not island:
        return None

    raw_props = island.get("props")
    if not raw_props:
        return None

    try:
        props = json.loads(html_lib.unescape(raw_props))
    except json.JSONDecodeError:
        return None

    decoded = _decode_astro_value(props)
    return decoded if isinstance(decoded, dict) else None


def _spot_name_from_astro(spot_meta: dict | None) -> str | None:
    """Extract the spot name from SpotMeta Astro props."""
    if not isinstance(spot_meta, dict):
        return None

    spot = spot_meta.get("spot")
    if not isinstance(spot, dict):
        return None

    name = spot.get("n")
    return str(name).strip() if name else None


def _parse_astro_update_info(
    soup: BeautifulSoup,
    forecast_type: str,
    spot_meta: dict | None,
    local_tz: timezone,
) -> tuple[str | None, str | None]:
    """Parse last/next update timestamps from Astro props or metadata fallback."""
    props = _astro_component_props(soup, "ForecastUpdateInfo")
    last_update = (
        _parse_http_datetime(props.get("lastUpdate"), local_tz)
        if isinstance(props, dict)
        else None
    )
    next_update = (
        _parse_http_datetime(props.get("expires"), local_tz)
        if isinstance(props, dict)
        else None
    )

    if next_update is None:
        next_update = _next_update_from_spot_meta(
            spot_meta,
            forecast_type,
            last_update,
            local_tz,
        )

    return last_update, next_update


def _parse_astro_forecast_data(
    soup: BeautifulSoup,
    local_tz: timezone,
) -> list[dict]:
    """Parse forecast rows from Windfinder's structured Astro props."""
    props = _astro_component_props(soup, "ForecastDataInit")
    if not isinstance(props, dict):
        return []

    fc_section_data = props.get("fcSectionData")
    forecasts: list[dict] = []

    for day in _iter_astro_forecast_days(fc_section_data):
        horizons = day.get("horizons")
        if not isinstance(horizons, list):
            continue

        for horizon in horizons:
            if not isinstance(horizon, dict):
                continue

            fc_data = horizon.get("fcData")
            if not isinstance(fc_data, dict):
                continue

            dt_iso = _normalize_datetime(
                fc_data.get("dt") or fc_data.get("dtl"),
                local_tz,
            )
            if not dt_iso:
                continue

            tide_data = horizon.get("tideData")
            has_wave_data = bool(horizon.get("hasWaveData"))
            has_tide_data = bool(horizon.get("hasTideData"))

            forecasts.append(
                {
                    "datetime": dt_iso,
                    "wind_speed_kn": _mps_to_knots(fc_data.get("ws")),
                    "wind_gust_kn": _mps_to_knots(fc_data.get("wg")),
                    "wind_direction_deg": _as_float(fc_data.get("wd")),
                    "wind_direction": None,
                    "temperature_c": _kelvin_to_c(fc_data.get("at")),
                    "feels_like_c": _kelvin_to_c(fc_data.get("fl")),
                    "rain_mm": _as_float(fc_data.get("p"), default=0),
                    "precipitation_type": fc_data.get("pt"),
                    "wave_direction_deg": (
                        _as_float(fc_data.get("wad")) if has_wave_data else None
                    ),
                    "wave_height_m": (
                        _as_float(fc_data.get("wah")) if has_wave_data else None
                    ),
                    "wave_interval_s": (
                        _as_int(fc_data.get("wap")) if has_wave_data else None
                    ),
                    "night_hour": bool(horizon.get("isNight")),
                    "cloud_cover_pct": _normalize_cloud_cover_pct(fc_data.get("cl")),
                    "relative_humidity_pct": _as_int(fc_data.get("rh")),
                    "air_pressure_hpa": _as_float(fc_data.get("ap")),
                    "tide_datetime": (
                        _normalize_datetime(tide_data.get("dtl"), local_tz)
                        if has_tide_data and isinstance(tide_data, dict)
                        else None
                    ),
                    "tide_type": (
                        tide_data.get("tp")
                        if has_tide_data and isinstance(tide_data, dict)
                        else None
                    ),
                    "tide_height_m": (
                        _as_float(tide_data.get("th"))
                        if has_tide_data and isinstance(tide_data, dict)
                        else None
                    ),
                }
            )

    return forecasts


def _iter_astro_forecast_days(node):
    """Yield day objects from nested Astro forecast data."""
    if isinstance(node, dict):
        horizons = node.get("horizons")
        if isinstance(horizons, list):
            yield node
        return

    if isinstance(node, list):
        for item in node:
            yield from _iter_astro_forecast_days(item)


def _next_update_from_spot_meta(
    spot_meta: dict | None,
    forecast_type: str,
    last_update: str | None,
    local_tz: timezone,
) -> str | None:
    """Approximate the next model update from SpotMeta when page update info is absent."""
    if not isinstance(spot_meta, dict):
        return None

    spot = spot_meta.get("spot")
    if not isinstance(spot, dict):
        return None

    forecast_products = spot.get("forecast_products")
    if not isinstance(forecast_products, list):
        return None

    product_id = "sfc" if forecast_type == "superforecast" else "gfs"
    last_update_dt = None
    if last_update:
        try:
            last_update_dt = datetime.fromisoformat(last_update)
        except ValueError:
            last_update_dt = None

    for product in forecast_products:
        if not isinstance(product, dict) or product.get("id") != product_id:
            continue

        candidate_times: list[datetime] = []
        forecast_models = product.get("forecast_models")
        if not isinstance(forecast_models, list):
            continue

        for model in forecast_models:
            if not isinstance(model, dict):
                continue
            for raw_update in model.get("update_times") or []:
                normalized = _normalize_datetime(raw_update, local_tz)
                if not normalized:
                    continue
                try:
                    candidate_times.append(datetime.fromisoformat(normalized))
                except ValueError:
                    continue

        if not candidate_times:
            continue

        candidate_times.sort()
        if last_update_dt:
            for candidate in candidate_times:
                if candidate > last_update_dt:
                    return candidate.isoformat()
            return (candidate_times[0] + timedelta(days=1)).isoformat()

        return candidate_times[0].isoformat()

    return None


def _parse_fc_day_rows(
    soup: BeautifulSoup,
    local_tz: timezone,
    known_datetimes: list[str] | None = None,
) -> list[dict]:
    """Parse current Windfinder day/row markup."""
    forecasts: list[dict] = []
    seen_datetimes: set[str] = set()
    now = datetime.now(local_tz)
    for day in soup.select(".fc-day"):
        headline = _first_text(day, (".fc-day-headline span", ".fc-day-headline"))
        parsed_date = _parse_headline_date(headline, now) if headline else None

        # Parse all horizon rows, not only a specific responsive variant.
        for row in day.select(".fc-table-horizon"):
            hour_text = _first_text(row, (".cell-ts",))
            hour = _extract_hour(hour_text)
            dt_iso = _row_datetime_iso(row, local_tz)
            if dt_iso is None:
                if parsed_date is None or hour is None:
                    continue
                dt_local = datetime(
                    parsed_date.year,
                    parsed_date.month,
                    parsed_date.day,
                    hour,
                    tzinfo=local_tz,
                )
                dt_iso = dt_local.astimezone(timezone.utc).isoformat()

            # Multiple responsive tables can contain the same timestamp.
            if dt_iso in seen_datetimes:
                continue
            seen_datetimes.add(dt_iso)

            wind_dir_title = None
            for child in row.find_all("div", recursive=False):
                classes = child.get("class", [])
                if "cell-wd" in classes:
                    wind_dir_title = child.select_one("svg title")
                    break

            forecasts.append(
                {
                    "datetime": dt_iso,
                    "wind_speed_kn": _as_float(_first_text(row, (".cell-ws .unit", ".cell-ws"))),
                    "wind_gust_kn": _as_float(_first_text(row, (".cell-wg .unit", ".cell-wg"))),
                    "wind_direction_deg": _svg_title_to_float(wind_dir_title),
                    "wind_direction": None,
                    "temperature_c": _as_float(_first_text(row, (".cell-at .unit", ".cell-at"))),
                    "feels_like_c": _as_float(_first_text(row, (".cell-fl .unit", ".cell-fl"))),
                    "rain_mm": _as_float(_first_text(row, (".cell-p .unit", ".cell-p")), default=0),
                    "wave_direction_deg": _svg_title_to_float(
                        row.select_one(".cell-waves-wrapper .cell-wd svg title")
                    ),
                    "wave_height_m": _as_float(_first_text(row, (".cell-wh",))),
                    "wave_interval_s": _as_int(_first_text(row, (".cell-wp",))),
                    "night_hour": "is-night" in row.get("class", []),
                    "cloud_cover_pct": _as_int(_first_text(row, (".cell-cl .unit", ".cell-cl"))),
                    "relative_humidity_pct": _as_int(
                        _first_text(row, (".cell-hum .unit", ".cell-hum"))
                    ),
                    "air_pressure_hpa": _as_float(_first_text(row, (".cell-ap",))),
                    "tide_datetime": _row_time_to_iso(
                        dt_iso,
                        _first_text(row, (".cell-tide-time .unit", ".cell-tide-time")),
                        local_tz,
                    ),
                    "tide_height_m": _as_float(
                        _first_text(row, (".cell-th .unit", ".cell-th"))
                    ),
                }
            )

    if forecasts:
        return forecasts

    known_hours: list[tuple[str, int]] = []
    if known_datetimes:
        for dt_iso in known_datetimes:
            try:
                dt_local = datetime.fromisoformat(dt_iso).astimezone(local_tz)
            except ValueError:
                continue
            known_hours.append((dt_iso, dt_local.hour))

    known_index = 0
    for row in soup.select(".fc-table-horizon.visible-md"):
        hour_text = _first_text(row, (".cell-ts",))
        hour = _extract_hour(hour_text)
        if hour is None:
            continue

        dt_iso = _row_datetime_iso(row, local_tz)
        if dt_iso is None and known_hours:
            while known_index < len(known_hours):
                candidate_iso, candidate_hour = known_hours[known_index]
                known_index += 1
                if candidate_hour == hour:
                    dt_iso = candidate_iso
                    break

        if dt_iso is None or dt_iso in seen_datetimes:
            continue
        seen_datetimes.add(dt_iso)

        wind_dir_title = None
        for child in row.find_all("div", recursive=False):
            classes = child.get("class", [])
            if "cell-wd" in classes:
                wind_dir_title = child.select_one("svg title")
                break

        forecasts.append(
            {
                "datetime": dt_iso,
                "wind_speed_kn": _as_float(_first_text(row, (".cell-ws .unit", ".cell-ws"))),
                "wind_gust_kn": _as_float(_first_text(row, (".cell-wg .unit", ".cell-wg"))),
                "wind_direction_deg": _svg_title_to_float(wind_dir_title),
                "wind_direction": None,
                "temperature_c": _as_float(_first_text(row, (".cell-at .unit", ".cell-at"))),
                "feels_like_c": _as_float(_first_text(row, (".cell-fl .unit", ".cell-fl"))),
                "rain_mm": _as_float(_first_text(row, (".cell-p .unit", ".cell-p")), default=0),
                "wave_direction_deg": _svg_title_to_float(
                    row.select_one(".cell-waves-wrapper .cell-wd svg title")
                ),
                "wave_height_m": _as_float(_first_text(row, (".cell-wh",))),
                "wave_interval_s": _as_int(_first_text(row, (".cell-wp",))),
                "night_hour": "is-night" in row.get("class", []),
                "cloud_cover_pct": _as_int(_first_text(row, (".cell-cl .unit", ".cell-cl"))),
                "relative_humidity_pct": _as_int(
                    _first_text(row, (".cell-hum .unit", ".cell-hum"))
                ),
                "air_pressure_hpa": _as_float(_first_text(row, (".cell-ap",))),
                "tide_datetime": _row_time_to_iso(
                    dt_iso,
                    _first_text(row, (".cell-tide-time .unit", ".cell-tide-time")),
                    local_tz,
                ),
                "tide_height_m": _as_float(
                    _first_text(row, (".cell-th .unit", ".cell-th"))
                ),
            }
        )

    return forecasts


def _parse_astro_layout_data(soup: BeautifulSoup, local_tz: timezone) -> list[dict]:
    """Parse the full forecast horizon from Windfinder's Astro island props."""
    props = _astro_component_props(soup, "FcTableWindpreviewContainer")
    if not isinstance(props, dict):
        return []

    layout_data = props.get("layoutData")
    if not isinstance(layout_data, list):
        return []

    forecasts: list[dict] = []
    for day in _iter_astro_forecast_days(layout_data):
        horizons = day.get("horizons")

        for horizon in horizons:
            if not isinstance(horizon, dict):
                continue
            dt_iso = _normalize_datetime(horizon.get("dtl"), local_tz)
            if not dt_iso:
                continue

            forecasts.append(
                {
                    "datetime": dt_iso,
                    "wind_speed_kn": _mps_to_knots(horizon.get("ws")),
                    "wind_gust_kn": _mps_to_knots(horizon.get("wg")),
                    "wind_direction_deg": _as_float(horizon.get("wd")),
                    "wind_direction": None,
                    "temperature_c": None,
                    "rain_mm": 0,
                    "wave_direction_deg": None,
                    "wave_height_m": None,
                    "wave_interval_s": None,
                    "night_hour": False,
                    "cloud_cover_pct": None,
                    "air_pressure_hpa": None,
                }
            )

    return forecasts


def _decode_astro_value(value):
    """Decode Astro's serialized prop wrapper format."""
    if isinstance(value, list) and len(value) == 2 and value[0] in (0, 1):
        return _decode_astro_value(value[1])
    if isinstance(value, list):
        return [_decode_astro_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _decode_astro_value(item) for key, item in value.items()}
    return value


def _combine_forecasts(*sources: list[dict]) -> list[dict]:
    """Union forecast sources by timestamp, preferring later sources."""
    source_maps: list[dict[str, dict]] = []
    all_datetimes: set[str] = set()

    for source in sources:
        mapping = {
            item["datetime"]: item
            for item in source
            if isinstance(item, dict) and item.get("datetime")
        }
        source_maps.append(mapping)
        all_datetimes.update(mapping)

    combined: list[dict] = []
    for dt_iso in sorted(all_datetimes):
        merged = {"datetime": dt_iso}
        for mapping in source_maps:
            item = mapping.get(dt_iso)
            if not item:
                continue
            for key, value in item.items():
                if key == "datetime" or value is None:
                    continue
                merged[key] = value
        combined.append(merged)

    return combined


def _row_datetime_iso(row, local_tz: timezone) -> str | None:
    """Extract a row datetime from common Windfinder data attributes."""
    for key in ("data-ts", "data-time", "data-timestamp", "data-dt", "datetime"):
        value = row.get(key)
        if value in (None, ""):
            continue
        if isinstance(value, Number) or str(value).strip().isdigit():
            timestamp = float(value)
            # Milliseconds are sometimes used for JS timestamps.
            if timestamp > 1_000_000_000_000:
                timestamp /= 1000
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.isoformat()
        normalized = _normalize_datetime(value, local_tz)
        if normalized:
            return normalized
    return None


def _extract_hour(value: str | None) -> int | None:
    """Extract an hour from strings like '02h'."""
    if not value:
        return None
    match = re.search(r"(\d{1,2})", value)
    if not match:
        return None
    hour = int(match.group(1))
    return hour if 0 <= hour <= 23 else None


def _svg_title_to_float(node) -> float | None:
    """Extract a degree value from an SVG title element."""
    if not node or not node.text:
        return None
    return _as_float(node.text.replace("°", ""))


def _normalize_datetime(value, local_tz: timezone) -> str | None:
    """Normalize datetime-like values to UTC ISO strings."""
    if value is None:
        return None
    if isinstance(value, Number):
        dt = datetime.fromtimestamp(float(value), tz=timezone.utc)
        return dt.isoformat()
    text = str(value).strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)
    return dt.astimezone(timezone.utc).isoformat()


def _parse_http_datetime(value, local_tz: timezone) -> str | None:
    """Parse HTTP-style datetimes such as 'Sun, 05 Apr 2026 10:35:57 GMT'."""
    if value is None:
        return None

    try:
        dt = parsedate_to_datetime(str(value).strip())
    except (TypeError, ValueError, IndexError):
        return _normalize_datetime(value, local_tz)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _row_time_to_iso(
    base_dt_iso: str | None,
    value: str | None,
    local_tz: timezone,
) -> str | None:
    """Attach a local HH:MM value to the closest day around a forecast row timestamp."""
    if not base_dt_iso or not value:
        return None

    match = re.search(r"(\d{1,2}):(\d{2})", value)
    if not match:
        return None

    try:
        base_local = datetime.fromisoformat(base_dt_iso).astimezone(local_tz)
    except ValueError:
        return None

    candidate = base_local.replace(
        hour=int(match.group(1)),
        minute=int(match.group(2)),
        second=0,
        microsecond=0,
    )
    delta = candidate - base_local
    if delta > timedelta(hours=12):
        candidate -= timedelta(days=1)
    elif delta < -timedelta(hours=12):
        candidate += timedelta(days=1)

    return candidate.astimezone(timezone.utc).isoformat()


def _kelvin_to_c(value, default=None):
    """Convert Kelvin values returned by Astro props into Celsius."""
    number = _as_float(value, default=None)
    if number is None:
        return default
    if number > 170:
        return round(number - 273.15, 2)
    return round(number, 2)


def _mps_to_knots(value, default=None):
    """Convert Windfinder's structured wind values from m/s to knots."""
    number = _as_float(value, default=None)
    if number is None:
        return default
    return round(number * MPS_TO_KNOTS, 2)


def _normalize_cloud_cover_pct(value):
    """Normalize cloud cover values to integer percentages."""
    number = _as_float(value, default=None)
    if number is None:
        return None
    if 0 <= number <= 1:
        number *= 100
    return int(round(number))


def _as_int(value, default=None):
    """Convert values to integer where possible."""
    number = _as_float(value, default=None)
    if number is None:
        return default
    return int(number)


def _as_float(value, default=None):
    """Convert a Windfinder value to float.

    Windfinder may return localized decimal separators or placeholders such
    as '-' in table cells; this helper normalizes such values.
    """
    if value is None:
        return default

    if isinstance(value, Number):
        return float(value)

    text = str(value).strip()
    if not text or text in {"-", "—", "–"}:
        return default

    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return default
