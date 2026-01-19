
#################################################################################################
# File:    sensor.py
# Version: 1.2 - Added matter_enabled attribute for Matter Server filtering
#################################################################################################

from typing import Any, Mapping

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entity import TeletaskEntity
from .teletask.device_config import SensorInfo

# Map sensor types to Home Assistant device classes and units
SENSOR_TYPE_CONFIG = {
    "temperature": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "default_unit": "°C",
    },
    "humidity": {
        "device_class": SensorDeviceClass.HUMIDITY,
        "state_class": SensorStateClass.MEASUREMENT,
        "default_unit": "%",
    },
    "illuminance": {
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "state_class": SensorStateClass.MEASUREMENT,
        "default_unit": "lx",
    },
    "power": {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "default_unit": "W",
    },
    "voltage": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "default_unit": "V",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up TeleTask analog sensors from config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]

    # Create entities from configured sensors (only where ha=True)
    sensors = hub.get_configured_sensors()
    entities = [TeletaskSensor(hub, sensor, entry.entry_id) for sensor in sensors if sensor.ha]

    async_add_entities(entities)


class TeletaskSensor(TeletaskEntity, SensorEntity):
    """Representation of a TeleTask analog sensor."""

    def __init__(self, hub, sensor: SensorInfo, entry_id: str) -> None:
        """Initialize the analog sensor."""
        super().__init__(hub, entry_id)
        self._num = sensor.num
        self._sensor = sensor

        # Set name from config (with room prefix if available)
        self._attr_name = sensor.display_name

        # Set device class and state class based on sensor type
        sensor_config = SENSOR_TYPE_CONFIG.get(sensor.type.lower(), {})
        if "device_class" in sensor_config:
            self._attr_device_class = sensor_config["device_class"]
        if "state_class" in sensor_config:
            self._attr_state_class = sensor_config["state_class"]

        # Set unit of measurement (use config unit or default)
        if sensor.unit:
            self._attr_native_unit_of_measurement = sensor.unit
        elif "default_unit" in sensor_config:
            self._attr_native_unit_of_measurement = sensor_config["default_unit"]

        # Set icon if configured
        if sensor.icon:
            self._attr_icon = f"mdi:{sensor.icon}" if not sensor.icon.startswith("mdi:") else sensor.icon

        # Set suggested area from room
        if sensor.room:
            self._attr_suggested_area = sensor.room

        self._attr_unique_id = f"teletask_{entry_id}_sensor_{sensor.num}"

    @property
    def native_value(self) -> float | None:
        """Return the current sensor value."""
        return self._hub.get_sensor_value(self._num)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes including Matter exposure flag."""
        return {
            "matter_enabled": self._sensor.matter,
            "teletask_function": 20,  # FUNC_SENSOR
            "teletask_number": self._num,
            "room": self._sensor.room,
        }
