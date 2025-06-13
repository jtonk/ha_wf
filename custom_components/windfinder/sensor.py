"""Windfinder sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

SENSOR_TYPES = {
    "speed": ["Wind Speed", "m/s"],
    "direction": ["Wind Direction", "°"],
    "gust": ["Wind Gust", "m/s"],
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [WindfinderSensor(coordinator, key) for key in SENSOR_TYPES]
    async_add_entities(entities)

class WindfinderSensor(SensorEntity):
    """Representation of a Windfinder sensor."""

    def __init__(self, coordinator, sensor_type: str):
        self.coordinator = coordinator
        self._attr_name = SENSOR_TYPES[sensor_type][0]
        self._attr_unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._sensor_type = sensor_type

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def state(self):
        data = self.coordinator.data or {}
        return data.get(self._sensor_type)

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
        attrs["speed"] = data.get("speed")
        attrs["direction"] = data.get("direction")
        attrs["gust"] = data.get("gust")
        return attrs
