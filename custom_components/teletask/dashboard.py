"""
Dashboard generator for TeleTask MICROS integration.

Creates a 3-tab dashboard:
1. Moods - General moods, Timed moods, and Local moods per area
2. Entities - All entities except moods, organized by area
3. Testing - TeleTask test card

The dashboard configuration is saved to HA's storage and registered as a sidebar item.
"""

import logging
import json
import os
from typing import Any, Dict, List
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.util import slugify
from homeassistant.components.lovelace import dashboard

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL = "teletask"
DASHBOARD_ICON = "mdi:home-automation"
STORAGE_KEY = f"lovelace.{DASHBOARD_URL}"
STORAGE_VERSION = 1


async def async_create_dashboard(
    hass: HomeAssistant,
    entry_id: str,
    device_name: str,
    device_config: Any
) -> None:
    """
    Create or update TeleTask dashboard.

    Args:
        hass: Home Assistant instance
        entry_id: Config entry ID
        device_name: Device name from devices.json
        device_config: DeviceConfig object
    """
    _LOGGER.info("Generating TeleTask dashboard configuration: %s", device_name)

    # Get entity registry
    entity_registry = er.async_get(hass)

    # Collect entities for this integration
    entities_by_area = {}  # area_name -> {domain -> [entity_ids]}
    mood_entities_by_area = {}  # area_name -> [mood entity_ids]
    general_moods = []
    timed_moods = []

    for entity_entry in er.async_entries_for_config_entry(entity_registry, entry_id):
        try:
            state = hass.states.get(entity_entry.entity_id)
            if not state:
                continue

            room = state.attributes.get("room", "")
            friendly_room = device_config.get_room_friendly_name(room) if room else "Other"
            domain = entity_entry.entity_id.split('.')[0]

            # Separate moods from other entities
            if domain == 'button':
                mood_type = state.attributes.get("mood_type", "")
                if mood_type == "GENERAL":
                    general_moods.append(entity_entry.entity_id)
                elif mood_type == "TIMED":
                    timed_moods.append(entity_entry.entity_id)
                else:  # LOCAL
                    if friendly_room not in mood_entities_by_area:
                        mood_entities_by_area[friendly_room] = []
                    mood_entities_by_area[friendly_room].append(entity_entry.entity_id)
            else:
                # Other entities (lights, switches, sensors, etc.)
                if friendly_room not in entities_by_area:
                    entities_by_area[friendly_room] = {}
                if domain not in entities_by_area[friendly_room]:
                    entities_by_area[friendly_room][domain] = []
                entities_by_area[friendly_room][domain].append(entity_entry.entity_id)

        except Exception as e:
            _LOGGER.warning("Failed to process entity %s: %s", entity_entry.entity_id, e)

    # Build dashboard configuration
    dashboard_config = {
        "views": [
            _generate_moods_tab(general_moods, timed_moods, mood_entities_by_area),
            _generate_entities_tab(entities_by_area),
            _generate_testing_tab()
        ]
    }

    # Save dashboard to storage
    try:
        store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        await store.async_save(dashboard_config)

        _LOGGER.info("TeleTask dashboard configuration saved to storage")

        # Register dashboard in lovelace config
        await _register_dashboard_in_config(hass, device_name)

    except Exception as e:
        _LOGGER.error("Failed to save dashboard: %s", e)
        import traceback
        _LOGGER.debug("Traceback: %s", traceback.format_exc())


async def _register_dashboard_in_config(hass: HomeAssistant, device_name: str) -> None:
    """Register dashboard in HA's lovelace configuration."""
    try:
        # Check if lovelace data is available
        if "lovelace" not in hass.data:
            _LOGGER.warning("Lovelace component not loaded, cannot register dashboard")
            return

        lovelace_data = hass.data["lovelace"]

        # Create dashboard configuration
        dashboard_config = {
            "mode": "storage",
            "title": device_name,
            "icon": DASHBOARD_ICON,
            "show_in_sidebar": True,
            "require_admin": False,
        }

        # Create LovelaceStorage instance
        lovelace_dashboard = dashboard.LovelaceStorage(hass, DASHBOARD_URL, dashboard_config)

        # Register dashboard
        lovelace_data["dashboards"][DASHBOARD_URL] = lovelace_dashboard

        _LOGGER.info(
            "\n"
            "="*70 + "\n"
            "TeleTask Dashboard Registered!\n"
            "="*70 + "\n"
            f"Dashboard '{device_name}' has been automatically added to your sidebar.\n"
            f"You can find it in the left menu with the {DASHBOARD_ICON} icon.\n"
            "="*70
        )
    except Exception as e:
        _LOGGER.error("Failed to register dashboard: %s", e)
        import traceback
        _LOGGER.debug("Traceback: %s", traceback.format_exc())


def _generate_moods_tab(
    general_moods: List[str],
    timed_moods: List[str],
    mood_entities_by_area: Dict[str, List[str]]
) -> Dict[str, Any]:
    """Generate Moods tab configuration."""
    cards = []

    # Panel 1: General Moods
    if general_moods:
        cards.append({
            "type": "entities",
            "title": "General Moods",
            "entities": general_moods,
            "state_color": True
        })

    # Panel 2: Timed Moods
    if timed_moods:
        cards.append({
            "type": "entities",
            "title": "Timed Moods",
            "entities": timed_moods,
            "state_color": True
        })

    # Panels 3+: Local Moods per area (sorted)
    for area_name in sorted(mood_entities_by_area.keys()):
        if mood_entities_by_area[area_name]:
            cards.append({
                "type": "entities",
                "title": f"{area_name} - Moods",
                "entities": mood_entities_by_area[area_name],
                "state_color": True
            })

    return {
        "title": "Moods",
        "icon": "mdi:lightbulb-group",
        "path": "moods",
        "cards": cards if cards else [{"type": "markdown", "content": "No moods configured"}]
    }


def _generate_entities_tab(
    entities_by_area: Dict[str, Dict[str, List[str]]]
) -> Dict[str, Any]:
    """Generate Entities tab configuration."""
    cards = []

    # One panel per area (sorted)
    for area_name in sorted(entities_by_area.keys()):
        area_entities = entities_by_area[area_name]

        # Flatten all entities for this area
        all_entities = []
        for domain in sorted(area_entities.keys()):
            all_entities.extend(area_entities[domain])

        if all_entities:
            cards.append({
                "type": "entities",
                "title": area_name,
                "entities": all_entities,
                "state_color": True
            })

    return {
        "title": "Entities",
        "icon": "mdi:devices",
        "path": "entities",
        "cards": cards if cards else [{"type": "markdown", "content": "No entities configured"}]
    }


def _generate_testing_tab() -> Dict[str, Any]:
    """Generate Testing tab with TeleTask test card."""
    return {
        "title": "Testing",
        "icon": "mdi:test-tube",
        "path": "testing",
        "cards": [
            {
                "type": "custom:teletask-test-card"
            }
        ]
    }


async def async_remove_dashboard(hass: HomeAssistant) -> None:
    """Remove TeleTask dashboard storage and unregister from lovelace."""
    try:
        # Remove from lovelace dashboards
        if "lovelace" in hass.data:
            lovelace_data = hass.data["lovelace"]
            if DASHBOARD_URL in lovelace_data.get("dashboards", {}):
                del lovelace_data["dashboards"][DASHBOARD_URL]
                _LOGGER.info("Unregistered TeleTask dashboard from sidebar")

        # Remove storage file
        store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        await store.async_remove()
        _LOGGER.info("Removed TeleTask dashboard storage")
    except Exception as e:
        _LOGGER.debug("Failed to remove dashboard (might not exist): %s", e)
