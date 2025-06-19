"""Windfinder integration."""

from __future__ import annotations

import logging

from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import aiohttp_client, config_validation as cv
import voluptuous as vol
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from bs4 import BeautifulSoup
import re
from datetime import datetime


from .const import (
    DOMAIN,
    CONF_LOCATION,
    FORECAST_URL,
    SUPERFORECAST_URL,
    PLATFORMS,
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
)

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

_LOGGER = logging.getLogger(__name__)

SERVICE_REFRESH = "refresh"
SERVICE_REFRESH_SCHEMA = vol.Schema({vol.Required(CONF_LOCATION): cv.string})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Windfinder component."""

    async def handle_refresh_service(call: ServiceCall) -> None:
        location = call.data[CONF_LOCATION].lower()
        for coordinator in hass.data.get(DOMAIN, {}).values():
            if getattr(coordinator, "_location", None) == location:
                await coordinator.async_request_refresh()
                return
        _LOGGER.warning("No Windfinder location '%s' found", call.data[CONF_LOCATION])

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

    refresh_minutes = entry.options.get(
        CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL
    )
    coordinator = WindfinderDataUpdateCoordinator(
        hass,
        session=session,
        location=entry.data[CONF_LOCATION],
        refresh_minutes=refresh_minutes,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
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

            async with self._session.get(
                superforecast_url, timeout=10
            ) as resp:
                resp.raise_for_status()
                superforecast_html = await resp.text()

            local_tz = (
                ZoneInfo(self.hass.config.time_zone)
                if self.hass.config.time_zone
                else timezone.utc
            )
            forecast = _parse_html(
                forecast_html, forecast_url, "forecast", local_tz
            )
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
    html: str, url: str, forecast_type: str, local_tz: timezone = timezone.utc
) -> dict:
    """Parse forecast HTML from Windfinder."""
    soup = BeautifulSoup(html, "html.parser")

    forecasts = []

    spot_name_el = soup.select_one("#spotheader-spotname")
    spot_name = spot_name_el.text.strip() if spot_name_el else None

    generated_at = None
    last_update = soup.select_one("#last-update")
    if last_update:
        m = re.match(r"(\d{1,2}):(\d{2})", last_update.text.strip())
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

    for day in soup.select(".forecast-day"):
        headline = day.select_one(".weathertable__headline")
        if not headline:
            continue
        clean = headline.text.replace(",", "").strip()
        parts = clean.split()
        if len(parts) < 3:
            continue
        try:
            month = MONTHS[parts[1]]
            day_num = int(parts[2])
        except (KeyError, ValueError):
            continue
        year = datetime.now(local_tz).year

        for row in day.select(".weathertable__row"):
            hour_el = row.select_one(".data-time .value")
            speed_el = row.select_one(".cell-wind-3 .units-ws")
            if not hour_el or not speed_el:
                continue
            hour_text = hour_el.text.strip()
            m = re.search(r"(\d+)", hour_text)
            if not m:
                continue
            hour = int(m.group(1))
            dt_local = datetime(year, month, day_num, hour, tzinfo=local_tz)
            dt = dt_local.astimezone(timezone.utc)

            gust_el = row.select_one(".cell-wind-3 .data-gusts .units-ws")
            dir_icon = row.select_one(".cell-wind-2 .icon-pointer-solid")
            dir_txt = row.select_one(".cell-wind-2 .units-wd-dir")

            dir_deg = None
            if dir_icon and dir_icon.has_attr("title"):
                try:
                    dir_deg = float(dir_icon["title"].replace("°", ""))
                except ValueError:
                    pass

            temp_el = row.select_one(".cell-weather-2 .data-temp .units-at")
            rain_el = row.select_one(".cell-weather-1 .data-rain .units-pr")
            wave_dir_el = row.select_one(".cell-waves-1 .directionarrow")
            wave_height_el = row.select_one(
                ".cell-waves-2 .data-waveheight .units-wh"
            )
            wave_freq_el = row.select_one(".cell-waves-2 .data-wavefreq")
            cloud_el = row.select_one(".data-cover .units-cl-perc")
            pressure_el = row.select_one(".data-pressure .units-ap")

            wave_dir = None
            if wave_dir_el and wave_dir_el.has_attr("style"):
                m = re.search(r"rotate\(([^)]+)deg\)", wave_dir_el["style"])

                if m:
                    wave_dir = float(m.group(1))

            wave_interval = None
            if wave_freq_el:
                m = re.search(r"(\d+)\s*s", wave_freq_el.text.strip())
                if m:
                    wave_interval = int(m.group(1))

            forecasts.append(
                {
                    "datetime": dt.isoformat(),
                    "wind_speed_kn": float(speed_el.text.strip()),
                    "wind_gust_kn": (
                        float(gust_el.text.strip()) if gust_el else None
                    ),
                    "wind_direction_deg": dir_deg,
                    "wind_direction": (
                        dir_txt.text.strip() if dir_txt else None
                    ),
                    "temperature_c": (
                        float(
                            temp_el.get("data-value") or temp_el.text.strip()
                        )
                        if temp_el
                        else None
                    ),
                    "rain_mm": (
                        float(
                            rain_el.get("data-value")
                            or rain_el.text.strip()
                            or 0
                        )
                        if rain_el
                        else 0
                    ),
                    "wave_direction_deg": wave_dir,
                    "wave_height_m": (
                        float(
                            wave_height_el.get("data-value")
                            or wave_height_el.text.strip()
                        )
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
                        float(
                            pressure_el.get("data-value")
                            or pressure_el.text.strip()
                        )
                        if pressure_el and pressure_el.text.strip()
                        else None
                    ),
                }
            )

    return {
        forecast_type + "data": forecasts,
        forecast_type + "_fetched": datetime.now(timezone.utc).isoformat(),
        forecast_type + "_generated": generated_at,
        "spot_name": spot_name,
    }
