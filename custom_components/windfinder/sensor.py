"""Windfinder sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime

from .const import DOMAIN, CONF_LOCATION


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WindfinderSensor(coordinator, entry)])


class WindfinderSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Windfinder sensor for one location."""

    _attr_should_poll = False
    _attr_icon = "mdi:windsock"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        location = entry.data[CONF_LOCATION]
        self._attr_name = f"Windfinder {location}"
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Windfinder {location}",
            manufacturer="Windfinder",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def state(self):
        data = self.coordinator.data or {}
        forecast_generated = data.get("forecast_generated")
        superforecast_generated = data.get("superforecast_generated")

        latest_dt = None
        for ts in (forecast_generated, superforecast_generated):
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    if not latest_dt or dt > latest_dt:
                        latest_dt = dt
                except ValueError:
                    pass

        if latest_dt:
            return latest_dt.isoformat()

        return superforecast_generated or forecast_generated

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        attrs = {}
        for key in (
            "forecastdata",
            "superforecastdata",
            "spot_name",
            "forecast_generated",
            "forecast_fetched",
            "superforecast_generated",
            "superforecast_fetched",
        ):
            if key in data:
                attrs[key] = data[key]
        return attrs
