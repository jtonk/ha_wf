"""Windfinder sensors."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

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
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_native_unit_of_measurement = UnitOfSpeed.KNOTS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._unsub_hourly_update: Callable[[], None] | None = None
        location = entry.data[CONF_LOCATION]
        self._attr_name = f"Windfinder {location}"
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Windfinder {location}",
            manufacturer="Windfinder",
        )

    async def async_added_to_hass(self) -> None:
        """Schedule local state updates for hourly forecast points."""
        await super().async_added_to_hass()
        self._schedule_next_hourly_update()

    async def async_will_remove_from_hass(self) -> None:
        """Cancel local state updates when the entity is removed."""
        self._cancel_hourly_update()
        await super().async_will_remove_from_hass()

    def _cancel_hourly_update(self) -> None:
        """Cancel the pending hourly state update."""
        if self._unsub_hourly_update is not None:
            self._unsub_hourly_update()
            self._unsub_hourly_update = None

    def _schedule_next_hourly_update(self) -> None:
        """Schedule the next state write at the top of the hour."""
        self._cancel_hourly_update()
        now = dt_util.utcnow()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(
            hours=1
        )
        self._unsub_hourly_update = async_track_point_in_utc_time(
            self.hass,
            self._handle_hourly_update,
            next_hour,
        )

    @callback
    def _handle_hourly_update(self, _now: datetime) -> None:
        """Write a new state when the active forecast hour changes."""
        self._unsub_hourly_update = None
        self.async_write_ha_state()
        self._schedule_next_hourly_update()

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        speed = _active_wind_speed(data, dt_util.utcnow())
        return round(speed, 1) if speed is not None else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        attrs = {}
        for key in (
            "forecastdata",
            "superforecastdata",
            "spot_name",
            "spot_timezone",
            "forecast_generated",
            "forecast_last_update",
            "forecast_next_update",
            "forecast_fetched",
            "superforecast_generated",
            "superforecast_last_update",
            "superforecast_next_update",
            "superforecast_fetched",
        ):
            if key in data:
                attrs[key] = data[key]
        return attrs


def _active_wind_speed(data: dict, now: datetime) -> float | None:
    """Return the active wind speed, preferring superforecast data."""
    for key in ("superforecastdata", "forecastdata"):
        speed = _active_wind_speed_from_forecasts(data.get(key), now)
        if speed is not None:
            return speed
    return None


def _active_wind_speed_from_forecasts(forecasts, now: datetime) -> float | None:
    """Return the forecast wind speed active at the current time."""
    if not isinstance(forecasts, list):
        return None

    now_utc = _as_utc(now)
    points: list[tuple[datetime, float]] = []

    for item in forecasts:
        if not isinstance(item, dict):
            continue

        timestamp = _parse_datetime(item.get("datetime"))
        speed = _as_float(item.get("wind_speed_kn"))
        if timestamp is None or speed is None:
            continue

        points.append((timestamp, speed))

    if not points:
        return None

    points.sort(key=lambda point: point[0])

    previous: tuple[datetime, float] | None = None
    for point in points:
        if point[0] > now_utc:
            return previous[1] if previous is not None else point[1]
        previous = point

    if previous is not None and now_utc - previous[0] <= timedelta(hours=1):
        return previous[1]

    return None


def _parse_datetime(value) -> datetime | None:
    """Parse an ISO timestamp as an aware UTC datetime."""
    if value is None:
        return None

    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None

    return _as_utc(dt)


def _as_utc(value: datetime) -> datetime:
    """Return a datetime as timezone-aware UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _as_float(value) -> float | None:
    """Convert a forecast value to float."""
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None
