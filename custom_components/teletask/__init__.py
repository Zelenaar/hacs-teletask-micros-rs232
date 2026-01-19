
#################################################################################################
# File:    __init__.py
# Version: 1.8.1 - Fixed TeleTask Test Card frontend resource registration
#
# TeleTask MICROS custom component for Home Assistant
#
# Frontend card (teletask-test-card.js) is registered programmatically via add_extra_js_url()
#################################################################################################

import logging
import serial

import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er, label_registry as lr
from homeassistant.components.frontend import add_extra_js_url

from .teletask_hub import TeletaskHub

_LOGGER = logging.getLogger(__name__)

DOMAIN = "teletask"
PLATFORMS = ["switch", "light", "number", "binary_sensor", "sensor", "button"]

# Label for Matter-enabled devices (used by Matterbridge add-on)
MATTER_LABEL_ID = "matterhomes"
MATTER_LABEL_NAME = "Matter Homes"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TeleTask hub from config entry."""
    try:
        # Create hub in executor to avoid blocking I/O in event loop
        hub = await hass.async_add_executor_job(TeletaskHub, hass, entry.data)
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

    # Register frontend resources (static path for Lovelace card)
    # Note: The card is primarily loaded via manifest.json frontend section
    # This provides an alternative access path for development/debugging
    _register_frontend_resources(hass)

    # Load platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    _register_services(hass, hub)

    # Assign matterhomes label to Matter-enabled entities
    await _async_assign_matter_labels(hass, entry, hub)

    return True


def _register_services(hass: HomeAssistant, hub: TeletaskHub) -> None:
    """Register TeleTask services."""

    def handle_set_mood(call):
        """Handle the set_mood service call."""
        number = call.data.get("number")
        mood_type = call.data.get("type", "LOCAL").upper()
        state = call.data.get("state", "ON").upper()

        # Map state string to value
        state_map = {"ON": 255, "OFF": 0, "TOGGLE": -1}
        state_value = state_map.get(state, 255)

        # Execute mood command based on type
        if mood_type == "LOCAL":
            if state_value == -1:
                hub.toggle_local_mood(number)
            else:
                hub.set_local_mood(number, state_value == 255)
        elif mood_type == "GENERAL":
            if state_value == -1:
                hub.toggle_general_mood(number)
            else:
                hub.set_general_mood(number, state_value == 255)
        else:
            _LOGGER.warning("Unknown mood type: %s", mood_type)

    def handle_set_flag(call):
        """Handle the set_flag service call."""
        number = call.data.get("number")
        state = call.data.get("state", "ON").upper()

        # Map state string to value
        state_map = {"ON": 255, "OFF": 0, "TOGGLE": -1}
        state_value = state_map.get(state, 255)

        if state_value == -1:
            hub.toggle_flag(number)
        else:
            hub.set_flag(number, state_value == 255)

    # Register services
    hass.services.register(DOMAIN, "set_mood", handle_set_mood)
    hass.services.register(DOMAIN, "set_flag", handle_set_flag)
    _LOGGER.info("Registered TeleTask services: set_mood, set_flag")


def _register_frontend_resources(hass: HomeAssistant) -> None:
    """Register JS resource for TeleTask Test Card."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    card_file = os.path.join(static_dir, "teletask-test-card.js")

    # Check if the card JS file exists
    if not os.path.exists(card_file):
        _LOGGER.debug("TeleTask Test Card JS not found at %s", card_file)
        return

    # Register static path using the app directly
    from aiohttp import web

    # Add static route to serve the card file
    hass.http.app.router.add_static(
        "/teletask_card",
        static_dir,
        name="teletask_card_static"
    )

    # Register the card JS as an extra module URL
    js_url = "/teletask_card/teletask-test-card.js"
    add_extra_js_url(hass, js_url)

    _LOGGER.info("Registered TeleTask Test Card: %s", js_url)


async def _async_assign_matter_labels(
    hass: HomeAssistant, entry: ConfigEntry, hub: TeletaskHub
) -> None:
    """Assign the 'matterhomes' label to all entities with matter=true."""
    # Get or create the matterhomes label
    label_registry = lr.async_get(hass)

    if not label_registry.async_get_label(MATTER_LABEL_ID):
        label_registry.async_create(
            name=MATTER_LABEL_NAME,
            label_id=MATTER_LABEL_ID,
            description="TeleTask devices exposed via Matter bridge",
            icon="mdi:home-automation",
        )
        _LOGGER.info("Created '%s' label for Matter-enabled devices", MATTER_LABEL_ID)

    # Collect all matter-enabled device numbers by type
    matter_devices = hub.get_matter_enabled_devices()
    if not matter_devices:
        _LOGGER.debug("No Matter-enabled devices configured")
        return

    # Get entity registry and update labels
    entity_registry = er.async_get(hass)
    entities_labeled = 0

    for entity_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        try:
            # Check if this entity should have the matter label
            should_label = _should_have_matter_label(entity_entry.unique_id, matter_devices)

            current_labels = set(entity_entry.labels or [])
            has_label = MATTER_LABEL_ID in current_labels

            if should_label and not has_label:
                # Add the label
                entity_registry.async_update_entity(
                    entity_entry.entity_id,
                    labels=current_labels | {MATTER_LABEL_ID}
                )
                entities_labeled += 1
                _LOGGER.debug("Added '%s' label to %s", MATTER_LABEL_ID, entity_entry.entity_id)
            elif not should_label and has_label:
                # Remove the label if matter was disabled
                entity_registry.async_update_entity(
                    entity_entry.entity_id,
                    labels=current_labels - {MATTER_LABEL_ID}
                )
                _LOGGER.debug("Removed '%s' label from %s", MATTER_LABEL_ID, entity_entry.entity_id)
        except Exception as e:
            _LOGGER.warning("Failed to update labels for %s: %s", entity_entry.entity_id, e)

    if entities_labeled:
        _LOGGER.info("Assigned '%s' label to %d entities", MATTER_LABEL_ID, entities_labeled)


def _should_have_matter_label(unique_id: str, matter_devices: dict) -> bool:
    """Check if an entity should have the matterhomes label based on its unique_id."""
    if not unique_id:
        return False

    # Parse unique_id format: teletask_{entry_id}_{type}_{num}
    # Examples: teletask_xxx_dimmer_1, teletask_xxx_relay_light_1, teletask_xxx_mood_local_1
    parts = unique_id.split("_")
    if len(parts) < 4 or parts[0] != "teletask":
        return False

    try:
        num = int(parts[-1])
        device_type = "_".join(parts[2:-1])  # Handle relay_light, relay_switch, mood_local, mood_general, etc.

        # Map entity types to config categories
        if device_type == "dimmer":
            return num in matter_devices.get("dimmers", set())
        elif device_type in ("relay_light", "relay_switch"):
            return num in matter_devices.get("relays", set())
        elif device_type == "flag":
            return num in matter_devices.get("flags", set())
        elif device_type == "input":
            return num in matter_devices.get("inputs", set())
        elif device_type == "sensor":
            return num in matter_devices.get("sensors", set())
        elif device_type in ("mood_local", "mood_general"):
            # Moods are stored in separate local/general dictionaries
            mood_type = "local_moods" if device_type == "mood_local" else "general_moods"
            return num in matter_devices.get(mood_type, set())
    except (ValueError, IndexError):
        pass

    return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload TeleTask config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]
    await hass.async_add_executor_job(hub.stop)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
