from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_LOCATION


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WindfinderRefreshButton(coordinator, entry)])


class WindfinderRefreshButton(ButtonEntity):
    """Button entity to manually refresh Windfinder data."""

    _attr_should_poll = False

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        self.coordinator = coordinator
        location = entry.data[CONF_LOCATION]
        self._attr_name = f"Refresh Windfinder {location}"
        self._attr_unique_id = f"{entry.entry_id}_refresh"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Windfinder {location}",
            manufacturer="Windfinder",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
