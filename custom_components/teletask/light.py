
#################################################################################################
# File:    light.py
# Version: 1.5 - Added matter_enabled attribute for Matter Server filtering
#################################################################################################

from typing import Any, Optional, Mapping

from homeassistant.components.light import LightEntity, ColorMode, ATTR_BRIGHTNESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entity import TeletaskEntity
from teletask.device_config import DeviceInfo

# Relay types that should be exposed as lights
LIGHT_TYPES = {"light", "lamp", "verlichting"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up TeleTask lights from config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Add dimmers as dimmable lights (only where ha=True)
    dimmers = hub.get_configured_dimmers()
    entities.extend([TeletaskDimmer(hub, dev, entry.entry_id) for dev in dimmers if dev.ha])

    # Add relays typed as "light" as on/off lights (only where ha=True)
    relays = hub.get_configured_relays()
    entities.extend([
        TeletaskRelayLight(hub, dev, entry.entry_id)
        for dev in relays
        if dev.ha and dev.type.lower() in LIGHT_TYPES
    ])

    async_add_entities(entities)


class TeletaskDimmer(TeletaskEntity, LightEntity):
    """Representation of a TeleTask dimmer light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, hub, device: DeviceInfo, entry_id: str) -> None:
        """Initialize the dimmer light."""
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

        self._attr_unique_id = f"teletask_{entry_id}_dimmer_{device.num}"

    @property
    def is_on(self) -> bool:
        """Return true if dimmer is on."""
        return self._hub.get_dimmer_value(self._num) > 0

    @property
    def brightness(self) -> Optional[int]:
        """Return the brightness of the dimmer (0-255)."""
        return self._hub.get_dimmer_value(self._num)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the dimmer on."""
        val = kwargs.get(ATTR_BRIGHTNESS, 255)
        await self.hass.async_add_executor_job(
            self._hub.set_dimmer_value, self._num, val
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the dimmer off."""
        await self.hass.async_add_executor_job(
            self._hub.set_dimmer_value, self._num, 0
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes including Matter exposure flag."""
        return {"matter_enabled": self._device.matter}


class TeletaskRelayLight(TeletaskEntity, LightEntity):
    """Representation of a TeleTask relay as an on/off light (no dimming)."""

    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, hub, device: DeviceInfo, entry_id: str) -> None:
        """Initialize the relay light."""
        super().__init__(hub, entry_id)
        self._num = device.num
        self._device = device

        # Set name from config (with room prefix if available)
        self._attr_name = device.display_name

        # Set icon if configured (default to lightbulb for lights)
        if device.icon:
            self._attr_icon = f"mdi:{device.icon}" if not device.icon.startswith("mdi:") else device.icon
        else:
            self._attr_icon = "mdi:lightbulb"

        # Set suggested area from room
        if device.room:
            self._attr_suggested_area = device.room

        self._attr_unique_id = f"teletask_{entry_id}_relay_light_{device.num}"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._hub.get_relay_state(self._num)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self.hass.async_add_executor_job(
            self._hub.set_relay_state, self._num, True
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.hass.async_add_executor_job(
            self._hub.set_relay_state, self._num, False
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes including Matter exposure flag."""
        return {"matter_enabled": self._device.matter}
