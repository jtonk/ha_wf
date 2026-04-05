"""Windfinder integration."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
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
from bs4 import BeautifulSoup


from .const import (
    CONF_LOCATION,
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
    FORECAST_URL,
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
            forecast = _parse_html(forecast_html, "forecast", local_tz)
            superforecast = _parse_html(
                superforecast_html,
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

    forecasts = _parse_astro_forecast_data(soup, local_tz)

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
    props_list = _astro_component_props_all(soup, component_name)
    return props_list[0] if props_list else None


def _astro_component_props_all(soup: BeautifulSoup, component_name: str) -> list[dict]:
    """Decode Astro component props for all matching component fragments."""
    decoded_props: list[dict] = []

    for island in soup.select(f"astro-island[component-url*='{component_name}']"):
        raw_props = island.get("props")
        if not raw_props:
            continue

        try:
            props = json.loads(html_lib.unescape(raw_props))
        except json.JSONDecodeError:
            continue

        decoded = _decode_astro_value(props)
        if isinstance(decoded, dict):
            decoded_props.append(decoded)

    return decoded_props


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
    forecasts: list[dict] = []

    props = _astro_component_props(soup, "ForecastDataInit")
    if isinstance(props, dict):
        forecasts = _combine_forecasts(
            forecasts,
            _parse_astro_forecast_rows(props.get("fcSectionData"), local_tz),
        )

    # Windfinder currently keeps today's full horizon in ForecastSection,
    # while ForecastDataInit can start at tomorrow 00:00.
    for props in _astro_component_props_all(soup, "ForecastSection"):
        forecasts = _combine_forecasts(
            forecasts,
            _parse_astro_forecast_rows(props.get("fcData"), local_tz),
        )

    return forecasts


def _parse_astro_forecast_rows(
    forecast_days,
    local_tz: timezone,
) -> list[dict]:
    """Parse forecast rows from a nested Astro day/horizon structure."""
    forecasts: list[dict] = []

    for day in _iter_astro_forecast_days(forecast_days):
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
                        _as_float(fc_data.get("wap")) if has_wave_data else None
                    ),
                    "night_hour": bool(horizon.get("isNight")),
                    "cloud_cover_pct": _normalize_cloud_cover_pct(fc_data.get("cl")),
                    "relative_humidity_pct": _as_float(fc_data.get("rh")),
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


def _kelvin_to_c(value, default=None):
    """Convert Kelvin values returned by Astro props into Celsius."""
    number = _as_float(value, default=None)
    if number is None:
        return default
    if number > 170:
        return number - 273.15
    return number


def _mps_to_knots(value, default=None):
    """Convert Windfinder's structured wind values from m/s to knots."""
    number = _as_float(value, default=None)
    if number is None:
        return default
    return number * MPS_TO_KNOTS


def _normalize_cloud_cover_pct(value):
    """Normalize cloud cover values to percentage scale without rounding."""
    number = _as_float(value, default=None)
    if number is None:
        return None
    if 0 <= number <= 1:
        number *= 100
    return number


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
