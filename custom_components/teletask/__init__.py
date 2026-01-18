
#################################################################################################
# File:    __init__.py
# Version: 1.2 - Added sensor platform for analog sensors
#
# TeleTask MICROS custom component for Home Assistant
#################################################################################################

import logging
import serial

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .teletask_hub import TeletaskHub

_LOGGER = logging.getLogger(__name__)

DOMAIN = "teletask"
PLATFORMS = ["switch", "light", "number", "binary_sensor", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TeleTask hub from config entry."""
    try:
        hub = TeletaskHub(hass, entry.data)
        await hass.async_add_executor_job(hub.start)
    except FileNotFoundError as e:
        _LOGGER.error("TeleTask config file not found: %s", e)
        raise ConfigEntryNotReady(f"Config file missing: {e}") from e
    except serial.SerialException as e:
        _LOGGER.error("TeleTask serial connection failed: %s", e)
        raise ConfigEntryNotReady(f"Serial connection failed: {e}") from e
    except ValueError as e:
        _LOGGER.error("TeleTask configuration error: %s", e)
        raise ConfigEntryNotReady(f"Configuration error: {e}") from e
    except Exception as e:
        _LOGGER.exception("TeleTask initialization failed unexpectedly")
        raise ConfigEntryNotReady(f"Initialization failed: {e}") from e

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = hub

    # Load platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload TeleTask config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]
    await hass.async_add_executor_job(hub.stop)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
