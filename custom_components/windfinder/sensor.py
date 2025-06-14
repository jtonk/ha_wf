"""Windfinder sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    async_add_entities([WindfinderSensor(coordinator, entry)])


class WindfinderSensor(SensorEntity):
    """Representation of a Windfinder sensor for one location."""

    def __init__(self, coordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        location = entry.data[CONF_LOCATION]
        self._attr_name = f"Windfinder {location}"
        self._attr_unit_of_measurement = None
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Windfinder {location}",
            manufacturer="Windfinder",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def state(self):
        data = self.coordinator.data or {}
        return data.get("general", {}).get("generated_at")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        attrs = {}
        if "forecastdata" in data:
            attrs["forecastdata"] = data["forecastdata"]
        if "superforecastdata" in data:
            attrs["superforecastdata"] = data["superforecastdata"]
        if "general" in data:
            attrs.update(data["general"])
        return attrs
