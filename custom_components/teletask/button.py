#################################################################################################
# File:    button.py
# Version: 1.0
#
# TeleTask mood button entities for Home Assistant.
# Moods are one-shot actions that configure multiple devices to preset states.
#################################################################################################

from typing import Any, Mapping

from homeassistant.components.button import ButtonEntity
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
    """Set up TeleTask mood buttons from config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]

    # Create button entities from configured moods (only where ha=True)
    moods = hub.get_configured_moods()
    entities = [TeletaskMoodButton(hub, mood, entry.entry_id) for mood in moods if mood.ha]

    async_add_entities(entities)


class TeletaskMoodButton(TeletaskEntity, ButtonEntity):
    """Representation of a TeleTask mood as a button entity."""

    def __init__(self, hub, device: DeviceInfo, entry_id: str) -> None:
        """Initialize the mood button."""
        super().__init__(hub, entry_id)
        self._num = device.num
        self._device = device
        self._mood_type = device.type.upper() if device.type else "LOCAL"

        # Set name from config (with room prefix if available)
        self._attr_name = device.display_name

        # Set icon if configured (default to lightbulb-group for moods)
        if device.icon:
            self._attr_icon = f"mdi:{device.icon}" if not device.icon.startswith("mdi:") else device.icon
        else:
            # Default icons based on mood type
            if self._mood_type == "GENERAL":
                self._attr_icon = "mdi:lightbulb-group"
            else:
                self._attr_icon = "mdi:lightbulb-group-outline"

        # Set suggested area from room
        if device.room:
            self._attr_suggested_area = device.room

        # Unique ID includes mood type to differentiate local vs general
        self._attr_unique_id = f"teletask_{entry_id}_mood_{self._mood_type.lower()}_{device.num}"

    async def async_press(self) -> None:
        """Trigger the mood (set to ON)."""
        await self.hass.async_add_executor_job(
            self._hub.trigger_mood, self._num, self._mood_type
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes including mood type and Matter exposure flag."""
        return {
            "mood_type": self._mood_type,
            "matter_enabled": self._device.matter
        }
