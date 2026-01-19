
#################################################################################################
# File:    number.py
# Version: 1.2
#################################################################################################

from typing import Optional

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entity import TeletaskEntity
from teletask.device_config import DeviceInfo


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up TeleTask dimmer number entities from config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]

    # Create entities from configured dimmers (only where ha=True)
    devices = hub.get_configured_dimmers()
    entities = [TeletaskDimmerNumber(hub, dev, entry.entry_id) for dev in devices if dev.ha]
    async_add_entities(entities)


class TeletaskDimmerNumber(TeletaskEntity, NumberEntity):
    """Numeric control (0-255) for TeleTask dimmers."""

    _attr_native_min_value = 0
    _attr_native_max_value = 255
    _attr_native_step = 1

    def __init__(self, hub, device: DeviceInfo, entry_id: str) -> None:
        """Initialize the dimmer number entity."""
        super().__init__(hub, entry_id)
        self._num = device.num
        self._device = device

        # Set name from config (with room prefix if available)
        self._attr_name = f"{device.display_name} Level"

        # Set icon if configured
        if device.icon:
            self._attr_icon = f"mdi:{device.icon}" if not device.icon.startswith("mdi:") else device.icon

        # Set suggested area from room
        if device.room:
            self._attr_suggested_area = device.room

        self._attr_unique_id = f"teletask_{entry_id}_dimmer_number_{device.num}"

    @property
    def native_value(self) -> Optional[float]:
        """Return the current dimmer value."""
        return self._hub.get_dimmer_value(self._num)

    async def async_set_native_value(self, value: float) -> None:
        """Set the dimmer value."""
        await self.hass.async_add_executor_job(
            self._hub.set_dimmer_value, self._num, int(value)
        )
