"""Windfinder integration."""

from __future__ import annotations

import logging

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_ENDPOINT, CONF_LOCATION, DEFAULT_ENDPOINT, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Windfinder component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Windfinder from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = aiohttp_client.async_get_clientsession(hass)

    coordinator = WindfinderDataUpdateCoordinator(
        hass,
        session=session,
        endpoint=entry.data.get(CONF_ENDPOINT, DEFAULT_ENDPOINT),
        location=entry.data[CONF_LOCATION],
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class WindfinderDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Node-RED."""

    def __init__(self, hass, *, session, endpoint, location):
        """Initialize coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=5))
        self._session = session
        self._endpoint = endpoint
        self._location = location

    async def _async_update_data(self):
        """Fetch data from Node-RED."""
        try:
            url = f"{self._endpoint}?location={self._location}"
            async with self._session.get(url, timeout=10) as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as err:
            raise UpdateFailed(err)
