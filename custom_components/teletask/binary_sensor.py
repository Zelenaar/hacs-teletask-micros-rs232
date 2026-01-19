
#################################################################################################
# File:    binary_sensor.py
# Version: 1.5 - Added matter_enabled attribute for Matter Server filtering
#################################################################################################

from typing import Any, Mapping

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entity import TeletaskEntity
from .teletask.device_config import DeviceInfo

# Map input types to Home Assistant device classes
INPUT_TYPE_DEVICE_CLASS = {
    "motion": BinarySensorDeviceClass.MOTION,
    "door": BinarySensorDeviceClass.DOOR,
    "window": BinarySensorDeviceClass.WINDOW,
    "smoke": BinarySensorDeviceClass.SMOKE,
    "occupancy": BinarySensorDeviceClass.OCCUPANCY,
    "presence": BinarySensorDeviceClass.PRESENCE,
    "button": None,  # No device class for buttons
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up TeleTask binary sensors (flags + physical inputs) from config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Create entities from configured flags (only where ha=True)
    flags = hub.get_configured_flags()
    entities.extend([TeletaskFlag(hub, dev, entry.entry_id) for dev in flags if dev.ha])

    # Create entities from configured inputs (only where ha=True)
    inputs = hub.get_configured_inputs()
    entities.extend([TeletaskInput(hub, dev, entry.entry_id) for dev in inputs if dev.ha])

    async_add_entities(entities)


class TeletaskFlag(TeletaskEntity, BinarySensorEntity):
    """Representation of a TeleTask flag as a binary sensor."""

    def __init__(self, hub, device: DeviceInfo, entry_id: str) -> None:
        """Initialize the flag binary sensor."""
        super().__init__(hub, entry_id)
        self._num = device.num
        self._device = device

        # Set name from config (with room prefix if available)
        self._attr_name = device.display_name

        # Set icon if configured
        if device.icon:
            self._attr_icon = f"mdi:{device.icon}" if not device.icon.startswith("mdi:") else device.icon

        # Set suggested area from room
        if device.room:
            self._attr_suggested_area = device.room

        self._attr_unique_id = f"teletask_{entry_id}_flag_{device.num}"

    @property
    def is_on(self) -> bool:
        """Return true if flag is on."""
        return self._hub.get_flag(self._num)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes including Matter exposure flag."""
        return {
            "matter_enabled": self._device.matter,
            "teletask_function": 15,  # FUNC_FLAG
            "teletask_number": self._num,
            "room": self._device.room,
        }


class TeletaskInput(TeletaskEntity, BinarySensorEntity):
    """Representation of a TeleTask physical input as a binary sensor."""

    def __init__(self, hub, device: DeviceInfo, entry_id: str) -> None:
        """Initialize the input binary sensor."""
        super().__init__(hub, entry_id)
        self._num = device.num
        self._device = device

        # Set name from config (with room prefix if available)
        self._attr_name = device.display_name

        # Set device class based on input type
        device_class = INPUT_TYPE_DEVICE_CLASS.get(device.type.lower())
        if device_class:
            self._attr_device_class = device_class

        # Set icon if configured
        if device.icon:
            self._attr_icon = f"mdi:{device.icon}" if not device.icon.startswith("mdi:") else device.icon

        # Set suggested area from room
        if device.room:
            self._attr_suggested_area = device.room

        self._attr_unique_id = f"teletask_{entry_id}_input_{device.num}"

    @property
    def is_on(self) -> bool:
        """Return true if input is active."""
        return self._hub.get_input_state(self._num)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes including Matter exposure flag."""
        return {
            "matter_enabled": self._device.matter,
            "teletask_function": 21,  # FUNC_INPUT
            "teletask_number": self._num,
            "room": self._device.room,
        }
