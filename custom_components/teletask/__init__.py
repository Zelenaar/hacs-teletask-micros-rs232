
#################################################################################################
# File:    __init__.py
# Version: 1.9.2 - Enhanced deduplication with tracking sets (hotfix for v1.14.1)
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
from homeassistant.helpers import entity_registry as er, label_registry as lr, area_registry as ar
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

    # Create areas from rooms and assign entities
    await _async_create_areas_and_assign_entities(hass, entry, hub)

    return True


def _register_services(hass: HomeAssistant, hub: TeletaskHub) -> None:
    """Register TeleTask services."""

    def handle_set_mood(call):
        """Handle the set_mood service call."""
        number = call.data.get("number")
        mood_type = call.data.get("type", "LOCAL").upper()
        state = call.data.get("state", "ON").upper()

        _LOGGER.info("set_mood called: number=%s, type=%s, state=%s", number, mood_type, state)

        # TeletaskHub only has trigger_mood() which sends ON
        # For ON state, trigger the mood
        if state == "ON":
            hub.trigger_mood(number, mood_type)
        else:
            # For OFF/TOGGLE, we need to call the client directly
            hub.client.set_mood(number, state, mood_type)

    def handle_set_flag(call):
        """Handle the set_flag service call."""
        number = call.data.get("number")
        state = call.data.get("state", "ON").upper()

        # Convert string state to boolean
        if state == "ON":
            hub.set_flag(number, True)
        elif state == "OFF":
            hub.set_flag(number, False)
        elif state == "TOGGLE":
            # Toggle by reading current state and flipping it
            current = hub.get_flag(number)
            hub.set_flag(number, not current)

    # Register services (check if already registered to prevent duplicates)
    if not hass.services.has_service(DOMAIN, "set_mood"):
        hass.services.async_register(DOMAIN, "set_mood", handle_set_mood)
        _LOGGER.info("Registered service: teletask.set_mood")

    if not hass.services.has_service(DOMAIN, "set_flag"):
        hass.services.async_register(DOMAIN, "set_flag", handle_set_flag)
        _LOGGER.info("Registered service: teletask.set_flag")


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

    # Check if route is already registered (prevents duplicate on reload)
    route_name = "teletask_card_static"
    route_exists = False
    for resource in hass.http.app.router.resources():
        if hasattr(resource, 'name') and resource.name == route_name:
            route_exists = True
            _LOGGER.debug("TeleTask card static route already registered, skipping")
            break

    # Only add route if it doesn't exist
    if not route_exists:
        hass.http.app.router.add_static(
            "/teletask_card",
            static_dir,
            name=route_name
        )
        _LOGGER.info("Registered TeleTask Test Card static route: /teletask_card")

    # Register the card JS as an extra module URL (idempotent, can be called multiple times)
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


async def _async_create_areas_and_assign_entities(
    hass: HomeAssistant, entry: ConfigEntry, hub: TeletaskHub
) -> None:
    """
    Create Home Assistant areas from device rooms and assign entities to them.

    This function:
    1. Extracts unique room names from devices.json
    2. Creates HA areas for each room (if not already exists)
    3. Assigns TeleTask entities to their corresponding areas based on room attribute
    """
    if not hub.device_config:
        _LOGGER.debug("No device config available, skipping area creation")
        return

    # Collect all unique rooms from device config
    unique_rooms = set()

    # Get rooms from all device types
    for relay in hub.device_config.get_all_relays():
        if relay.room:
            unique_rooms.add(relay.room)

    for dimmer in hub.device_config.get_all_dimmers():
        if dimmer.room:
            unique_rooms.add(dimmer.room)

    for mood in hub.device_config.get_all_moods():
        if mood.room:
            unique_rooms.add(mood.room)

    for flag in hub.device_config.get_all_flags():
        if flag.room:
            unique_rooms.add(flag.room)

    for input_device in hub.device_config.get_all_inputs():
        if input_device.room:
            unique_rooms.add(input_device.room)

    for sensor in hub.device_config.get_all_sensors():
        if sensor.room:
            unique_rooms.add(sensor.room)

    if not unique_rooms:
        _LOGGER.debug("No rooms found in device config, skipping area creation")
        return

    _LOGGER.info("Found %d unique rooms in device config", len(unique_rooms))

    # Get area registry
    area_registry = ar.async_get(hass)

    # Create areas for each room (if not already exists)
    # Map room name to area_id for entity assignment
    room_to_area_id = {}
    areas_created = 0

    for room_name in sorted(unique_rooms):
        # Get friendly name from rooms section (if available)
        display_name = hub.device_config.get_room_friendly_name(room_name)

        # Check if area with this display name already exists
        existing_area = None
        for area in area_registry.areas.values():
            if area.name == display_name:
                existing_area = area
                break

        if existing_area:
            # Area already exists, use it
            room_to_area_id[room_name] = existing_area.id
            _LOGGER.debug("Area '%s' already exists (ID: %s)", display_name, existing_area.id)
        else:
            # Create new area
            # Generate normalized area_id from display name (lowercase, replace spaces/special chars with underscores)
            area_id = display_name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
            # Remove consecutive underscores
            import re
            area_id = re.sub(r'_+', '_', area_id).strip('_')

            try:
                new_area = area_registry.async_create(
                    name=display_name,
                )
                room_to_area_id[room_name] = new_area.id
                areas_created += 1
                _LOGGER.info("Created area '%s' (ID: %s) from TeleTask room '%s'", display_name, new_area.id, room_name)
            except Exception as e:
                _LOGGER.warning("Failed to create area '%s': %s", display_name, e)

    if areas_created:
        _LOGGER.info("Created %d new areas from device rooms", areas_created)

    # Now assign entities to their areas
    # IMPORTANT: Deduplicate entities to avoid showing same device multiple times
    # For relays, prefer light entities over switch entities
    entity_registry = er.async_get(hass)
    entities_assigned = 0
    entities_unassigned = 0

    # Track which entity_ids we've already processed to prevent duplicates
    processed_entities = set()

    # First pass: collect all entities and group by device key
    # device_key = (teletask_function, teletask_number)
    device_entities = {}  # device_key -> [(entity_entry, state, room, domain)]
    unique_entities = {}  # entity_id -> (entity_entry, state, room, domain) for entities without device key

    for entity_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        try:
            # Skip if already processed (safety check)
            if entity_entry.entity_id in processed_entities:
                _LOGGER.warning("Entity %s already processed, skipping duplicate", entity_entry.entity_id)
                continue

            state = hass.states.get(entity_entry.entity_id)
            if not state:
                continue

            room = state.attributes.get("room")
            if not room or room not in room_to_area_id:
                continue

            teletask_number = state.attributes.get("teletask_number")
            teletask_function = state.attributes.get("teletask_function")
            domain = entity_entry.entity_id.split('.')[0]

            if teletask_number is None or teletask_function is None:
                # No device identifiers, store separately (these are unique)
                unique_entities[entity_entry.entity_id] = (entity_entry, state, room, domain)
                processed_entities.add(entity_entry.entity_id)
                continue

            # Group by device key
            device_key = (teletask_function, teletask_number)
            if device_key not in device_entities:
                device_entities[device_key] = []
            device_entities[device_key].append((entity_entry, state, room, domain))
            processed_entities.add(entity_entry.entity_id)

        except Exception as e:
            _LOGGER.warning("Failed to process entity %s: %s", entity_entry.entity_id, e)

    # Assign unique entities (those without device keys)
    for entity_id, (entity_entry, state, room, domain) in unique_entities.items():
        try:
            target_area_id = room_to_area_id[room]
            if entity_entry.area_id != target_area_id:
                entity_registry.async_update_entity(
                    entity_entry.entity_id,
                    area_id=target_area_id
                )
                entities_assigned += 1
                _LOGGER.debug("Assigned unique entity %s to area '%s'", entity_entry.entity_id, room)
        except Exception as e:
            _LOGGER.warning("Failed to assign unique entity %s: %s", entity_id, e)

    # Second pass: for each device, select ONE preferred entity and assign ONLY that one
    assigned_device_entities = set()  # Track which entity_ids got assigned to areas

    for device_key, entities in device_entities.items():
        try:
            teletask_function, teletask_number = device_key

            # Select preferred entity
            # For relays (function=1), prefer light over switch
            # For others, just take the first one
            preferred_entity = entities[0]

            if teletask_function == 1 and len(entities) > 1:
                # Relay with multiple entities, prefer light
                for entity_data in entities:
                    entity_entry, state, room, domain = entity_data
                    if domain == 'light':
                        preferred_entity = entity_data
                        break

            entity_entry, state, room, domain = preferred_entity
            target_area_id = room_to_area_id[room]

            # Assign ONLY the preferred entity
            if entity_entry.area_id != target_area_id:
                entity_registry.async_update_entity(
                    entity_entry.entity_id,
                    area_id=target_area_id
                )
                entities_assigned += 1
                _LOGGER.debug("Assigned %s to area '%s' (preferred for device %s)",
                            entity_entry.entity_id, room, device_key)

            # Mark this entity as assigned
            assigned_device_entities.add(entity_entry.entity_id)

        except Exception as e:
            _LOGGER.warning("Failed to assign device %s to area: %s", device_key, e)

    # Third pass: Unassign ALL non-preferred entities for each device
    for device_key, entities in device_entities.items():
        for entity_data in entities:
            other_entry, _, _, _ = entity_data
            # If this entity wasn't marked as assigned AND has an area, remove it
            if other_entry.entity_id not in assigned_device_entities and other_entry.area_id is not None:
                entity_registry.async_update_entity(
                    other_entry.entity_id,
                    area_id=None
                )
                entities_unassigned += 1
                _LOGGER.debug("Unassigned duplicate entity %s from areas", other_entry.entity_id)

    if entities_assigned:
        _LOGGER.info("Assigned %d entities to their rooms (areas)", entities_assigned)
    if entities_unassigned:
        _LOGGER.info("Unassigned %d duplicate entities from areas", entities_unassigned)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload TeleTask config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]
    await hass.async_add_executor_job(hub.stop)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
