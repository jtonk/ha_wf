"""Windfinder integration."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
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

    forecasts = []

    spot_name = _first_text(
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

    generated_at = None
    # Windfinder only provides the hour and minute of the last update.
    last_update = _first_text(
        soup,
        (
            "#last-update",
            "[data-testid='last-update']",
            ".last-update",
        ),
    )
    if last_update:
        m = re.search(r"(\d{1,2}):(\d{2})", last_update)
        if m:
            now = datetime.now(local_tz)
            dt_local = datetime(
                now.year,
                now.month,
                now.day,
                int(m.group(1)),
                int(m.group(2)),
                tzinfo=local_tz,
            )
            generated_at = dt_local.astimezone(timezone.utc).isoformat()

    now = datetime.now(local_tz)

    for day in soup.select(".forecast-day, .weathertable, [data-testid='forecast-day']"):
        headline = day.select_one(
            ".weathertable__headline, .forecast-day__headline, [data-testid='day-headline']"
        )
        if not headline:
            continue
        parsed_date = _parse_headline_date(headline.text, now)
        if not parsed_date:
            # Skip rows that do not contain a valid date
            continue

        for row in day.select(".weathertable__row, tr, [data-testid='forecast-row']"):
            hour_text = _first_text(
                row,
                (
                    ".data-time .value",
                    ".cell-time .value",
                    ".data-time",
                    "[data-testid='hour']",
                ),
            )
            speed_text = _first_text(
                row,
                (
                    ".cell-wind-3 .units-ws",
                    ".data-wind .units-ws",
                    "[data-testid='wind-speed']",
                ),
            ) or row.get("data-wind-speed")

            if not hour_text or speed_text is None:
                continue
            # Extract hour and build a timezone-aware datetime
            m = re.search(r"(\d+)", hour_text)
            if not m:
                continue
            hour = int(m.group(1))
            dt_local = datetime(
                parsed_date.year,
                parsed_date.month,
                parsed_date.day,
                hour,
                tzinfo=local_tz,
            )
            dt = dt_local.astimezone(timezone.utc)

            gust_text = _first_text(
                row,
                (
                    ".cell-wind-3 .data-gusts .units-ws",
                    "[data-testid='wind-gust']",
                ),
            ) or row.get("data-wind-gust")
            dir_icon = row.select_one(".cell-wind-2 .icon-pointer-solid")
            dir_txt = _first_text(
                row,
                (
                    ".cell-wind-2 .units-wd-dir",
                    "[data-testid='wind-direction']",
                ),
            )

            dir_deg = None
            if dir_icon and dir_icon.has_attr("title"):
                try:
                    dir_deg = float(dir_icon["title"].replace("°", ""))
                except ValueError:
                    pass
            if dir_deg is None:
                dir_deg = _as_float(row.get("data-wind-direction-deg"))

            temp_el = row.select_one(".cell-weather-2 .data-temp .units-at")
            rain_el = row.select_one(".cell-weather-1 .data-rain .units-pr")
            wave_dir_el = row.select_one(".cell-waves-1 .directionarrow")
            wave_height_el = row.select_one(".cell-waves-2 .data-waveheight .units-wh")
            wave_freq_el = row.select_one(".cell-waves-2 .data-wavefreq")
            cloud_el = row.select_one(".data-cover .units-cl-perc")
            pressure_el = row.select_one(".data-pressure .units-ap")

            wave_dir = None
            # Direction arrow uses a CSS rotate() transform
            if wave_dir_el and wave_dir_el.has_attr("style"):
                m = re.search(r"rotate\(([^)]+)deg\)", wave_dir_el["style"])

                if m:
                    wave_dir = float(m.group(1))

            wave_interval = None
            if wave_freq_el:
                # Extract interval from text like "8 s"
                m = re.search(r"(\d+)\s*s", wave_freq_el.text.strip())
                if m:
                    wave_interval = int(m.group(1))

            forecasts.append(
                {
                    "datetime": dt.isoformat(),
                    "wind_speed_kn": _as_float(speed_text),
                    "wind_gust_kn": _as_float(gust_text),
                    "wind_direction_deg": dir_deg,
                    "wind_direction": dir_txt,
                    "temperature_c": (
                        _as_float(temp_el.get("data-value") or temp_el.text)
                        if temp_el
                        else None
                    ),
                    "rain_mm": (
                        _as_float(rain_el.get("data-value") or rain_el.text, default=0)
                        if rain_el
                        else 0
                    ),
                    "wave_direction_deg": wave_dir,
                    "wave_height_m": (
                        _as_float(wave_height_el.get("data-value") or wave_height_el.text)
                        if wave_height_el
                        else None
                    ),
                    "wave_interval_s": wave_interval,
                    "night_hour": "row-stripe" in row.get("class", []),
                    "cloud_cover_pct": (
                        int(cloud_el.text.replace("%", "").strip())
                        if cloud_el and cloud_el.text.strip()
                        else None
                    ),
                    "air_pressure_hpa": (
                        _as_float(pressure_el.get("data-value") or pressure_el.text)
                        if pressure_el and pressure_el.text.strip()
                        else None
                    ),
                }
            )

    if not forecasts:
        forecasts = _parse_fc_day_rows(soup, local_tz)

    if not forecasts:
        _LOGGER.debug(
            "No rows parsed from %s HTML table, trying embedded JSON fallback", url
        )
        forecasts = _parse_embedded_json(soup, local_tz)

    # Bundle parsed results together with metadata
    return {
        forecast_type + "data": forecasts,
        forecast_type + "_fetched": datetime.now(timezone.utc).isoformat(),
        forecast_type + "_generated": generated_at,
        "spot_name": spot_name,
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


def _parse_fc_day_rows(soup: BeautifulSoup, local_tz: timezone) -> list[dict]:
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
                    "rain_mm": _as_float(_first_text(row, (".cell-p .unit", ".cell-p")), default=0),
                    "wave_direction_deg": _svg_title_to_float(
                        row.select_one(".cell-waves-wrapper .cell-wd svg title")
                    ),
                    "wave_height_m": _as_float(_first_text(row, (".cell-wh",))),
                    "wave_interval_s": _as_int(_first_text(row, (".cell-wp",))),
                    "night_hour": "is-night" in row.get("class", []),
                    "cloud_cover_pct": _as_int(_first_text(row, (".cell-cl .unit", ".cell-cl"))),
                    "air_pressure_hpa": _as_float(_first_text(row, (".cell-ap",))),
                }
            )

    return forecasts


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


def _parse_embedded_json(soup: BeautifulSoup, local_tz: timezone) -> list[dict]:
    """Fallback parser for newer Windfinder pages that expose data via JSON."""
    candidates: list[dict] = []
    for script in soup.select("script[type='application/ld+json'], script"):
        raw = script.string or script.text or ""
        raw = raw.strip()
        if "forecast" not in raw.lower() or "wind" not in raw.lower():
            continue
        payload = _extract_json(raw)
        if isinstance(payload, dict):
            candidates.append(payload)

    for payload in candidates:
        normalized = _normalize_payload_forecast(payload, local_tz)
        if normalized:
            return normalized
    return []


def _extract_json(raw: str) -> dict | None:
    """Best-effort extraction for JSON objects in script tags."""
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(1))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_payload_forecast(payload: dict, local_tz: timezone) -> list[dict]:
    """Normalize common JSON forecast structures into integration attributes."""
    rows = payload.get("forecast") or payload.get("forecastData") or payload.get("data")
    if not isinstance(rows, list):
        return []

    normalized: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        timestamp = row.get("datetime") or row.get("time") or row.get("timestamp")
        dt_iso = _normalize_datetime(timestamp, local_tz)
        if not dt_iso:
            continue

        normalized.append(
            {
                "datetime": dt_iso,
                "wind_speed_kn": _as_float(row.get("wind_speed_kn") or row.get("windSpeed")),
                "wind_gust_kn": _as_float(row.get("wind_gust_kn") or row.get("windGust")),
                "wind_direction_deg": _as_float(
                    row.get("wind_direction_deg") or row.get("windDirectionDeg")
                ),
                "wind_direction": row.get("wind_direction") or row.get("windDirection"),
                "temperature_c": _as_float(row.get("temperature_c") or row.get("temperature")),
                "rain_mm": _as_float(row.get("rain_mm") or row.get("rain"), default=0),
                "wave_direction_deg": _as_float(
                    row.get("wave_direction_deg") or row.get("waveDirectionDeg")
                ),
                "wave_height_m": _as_float(row.get("wave_height_m") or row.get("waveHeight")),
                "wave_interval_s": _as_float(
                    row.get("wave_interval_s") or row.get("waveInterval")
                ),
                "night_hour": bool(row.get("night_hour") or row.get("isNight")),
                "cloud_cover_pct": _as_int(
                    row.get("cloud_cover_pct") or row.get("cloudCover")
                ),
                "air_pressure_hpa": _as_float(
                    row.get("air_pressure_hpa") or row.get("pressure")
                ),
            }
        )
    return normalized


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
