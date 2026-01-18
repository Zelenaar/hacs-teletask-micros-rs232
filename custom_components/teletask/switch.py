
#################################################################################################
# File:    switch.py
# Version: 1.5 - Added matter_enabled attribute for Matter Server filtering
#################################################################################################

from typing import Any, Optional, Mapping

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entity import TeletaskEntity
from teletask.device_config import DeviceInfo

# Relay types that should be exposed as lights (not switches)
LIGHT_TYPES = {"light", "lamp", "verlichting"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up TeleTask relay switches from config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]

    # Create entities from configured relays, excluding those typed as lights
    # Only include devices where ha=True
    devices = hub.get_configured_relays()
    entities = [
        TeletaskRelay(hub, dev, entry.entry_id)
        for dev in devices
        if dev.ha and dev.type.lower() not in LIGHT_TYPES
    ]
    async_add_entities(entities)


class TeletaskRelay(TeletaskEntity, SwitchEntity):
    """Representation of a TeleTask relay switch."""

    def __init__(self, hub, device: DeviceInfo, entry_id: str) -> None:
        """Initialize the relay switch."""
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

        self._attr_unique_id = f"teletask_{entry_id}_relay_{device.num}"

    @property
    def is_on(self) -> bool:
        """Return true if relay is on."""
        return self._hub.get_relay_state(self._num)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the relay on."""
        await self.hass.async_add_executor_job(
            self._hub.set_relay_state, self._num, True
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the relay off."""
        await self.hass.async_add_executor_job(
            self._hub.set_relay_state, self._num, False
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes including Matter exposure flag."""
        return {"matter_enabled": self._device.matter}
