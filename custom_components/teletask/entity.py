
#################################################################################################
# File:    entity.py
# Version: 1.0
#
# Base entity class for TeleTask entities with device_info and availability.
#################################################################################################

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo

from . import DOMAIN


class TeletaskEntity(Entity):
    """Base class for TeleTask entities with shared device info and availability."""

    _attr_has_entity_name = True

    def __init__(self, hub, entry_id: str) -> None:
        """
        Initialize the TeleTask entity.

        Args:
            hub: TeletaskHub instance.
            entry_id: Config entry ID for unique identification.
        """
        self._hub = hub
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to group entities under a single device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="TeleTask MICROS",
            manufacturer="TeleTask",
            model="MICROS",
            sw_version="1.0",
        )

    @property
    def available(self) -> bool:
        """Return True if the hub is running and connected."""
        return self._hub.running
