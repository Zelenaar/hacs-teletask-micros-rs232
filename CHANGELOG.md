# Changelog

All notable changes to this project will be documented in this file.

## [1.13.0] - 2026-01-21

### Added
- **Auto-Create Areas from Rooms**: Integration now automatically creates Home Assistant areas based on room names in devices.json
  - Extracts unique room names from all device types (relays, dimmers, moods, flags, inputs, sensors)
  - Creates HA areas for each unique room if not already exists
  - Automatically assigns TeleTask entities to their corresponding areas based on room attribute
  - Areas are created with normalized IDs (lowercase, spaces/dashes replaced with underscores)
  - Safe: Only creates areas that don't exist, doesn't overwrite existing areas
  - Entities are only reassigned if they're not already in the correct area
  - **Result:** Better organization in Home Assistant UI, entities grouped by room automatically

### How It Works
1. During integration setup, reads all rooms from devices.json
2. Creates HA area for each unique room (e.g., "NG1-Orangerie", "NV1-Sl.K Ouders", "OG1-Bibliotheek")
3. Assigns each entity to its area based on the "room" attribute from devices.json
4. Logs creation/assignment actions for visibility

## [1.12.0] - 2026-01-21

### Fixed
- **CRITICAL: Swapped Function Codes for GENERAL and TIMED Moods**
  - Issue: GENERAL moods used function code 9, TIMED moods used function code 10
  - Correct: TIMED=9, GENERAL=10 (as per TeleTask protocol and PROSOFT)
  - Impact: GENERAL and TIMED moods were completely broken (sending wrong commands)
  - Files fixed:
    - `button.py`: Fixed func_map {"LOCAL": 8, "TIMED": 9, "GENERAL": 10}
    - `device-control-tab.ts`: Fixed function code checks for mood filtering
  - **All moods now work correctly with proper TeleTask protocol codes**

### Confirmed Working
- ✓ Room filtering works for all mood types (local, general, timed)
- ✓ Test card properly filters moods by teletask_function codes
- ✓ Backend button entities expose correct function codes in attributes
- ✓ device_config.py loads all three mood types from separate arrays

## [1.11.0] - 2026-01-21

### Fixed
- **Timed Moods Now Load from NBT Extraction**: Added `timed_moods` field to `device_config.py`
  - Issue: GUI NBT extraction tool creates `timed_moods` array in devices.json
  - Previous bug: `device_config.py` didn't recognize `timed_moods` field
  - Impact: Extracted timed moods weren't being loaded into Home Assistant
  - Solution: Added `timed_moods` field to DeviceConfig dataclass
  - Backward compatibility: Supports both old "moods" format and new separate keys

### Changed
- **Device Config (v1.4)**: Enhanced mood loading to support three separate mood types
  - Added `timed_moods` field to DeviceConfig
  - Updated `get_mood()` to handle TIMED type
  - Updated `get_all_moods()` to include timed moods
  - Supports loading from both formats:
    - Old: `"moods"` array with `"type"` field
    - New: Separate `"local_moods"`, `"general_moods"`, `"timed_moods"` arrays

## [1.10.0] - 2026-01-20

### Fixed
- **CRITICAL: Moods now work correctly**: Fixed "Mood SET not confirmed" error
  - Error: `RuntimeError: Mood SET not confirmed` when activating local/general/timed moods
  - Root cause: Moods are **trigger actions**, not stateful devices like relays/dimmers
  - Old code used `_set_with_confirm()` which waits for EVENT/GET state confirmation
  - TeleTask MICROS doesn't send EVENT for moods (they're triggers, not states)
  - TeleTask MICROS doesn't respond to GET for moods (no persistent state to query)
  - **Solution:** Rewrote `set_mood()` to treat moods as trigger actions
  - **Impact:** Local/General/Timed moods now activate correctly

### Technical Details

**What are Moods?**
Moods are **trigger actions** that execute pre-programmed scenes. Unlike relays (which have ON/OFF state), moods don't have persistent state - they just trigger an action and complete.

**Old (BROKEN) Logic:**
```python
def set_mood():
    ok = self._set_with_confirm(func, num, STATE_ON)  # Wait for EVENT/GET
    if not ok:
        raise RuntimeError("Mood SET not confirmed.")  # Always failed!
```

The confirmation logic was designed for stateful devices:
1. Send SET command
2. Wait for EVENT with new state
3. Fallback: GET the state to confirm
4. Retry if no confirmation

This doesn't work for moods because they don't emit EVENTs or respond to GET.

**New (WORKING) Logic:**
```python
def set_mood():
    # Send SET command (fire-and-forget for trigger actions)
    frame = self._compose_frame(CMD_SET, bytes([func, num, target]))
    self._send_frame(frame)

    # Wait briefly for ACK (optional, just confirms command received)
    ack_received = self._wait_ack(200)

    # Success - moods don't have state to confirm
```

Moods are now treated correctly as trigger actions:
- Send the command
- Optionally wait for ACK (command received confirmation)
- Return success immediately (don't wait for state that doesn't exist)

**Driver Version:** V06.2 → V06.3 (both HA and standalone)

## [1.9.13] - 2026-01-20

### Fixed
- **CRITICAL: Threading violation in event firing**: Fixed Home Assistant crash risk
  - Warning: "Detected that custom integration 'teletask' calls hass.bus.async_fire from a thread"
  - Location: teletask_hub.py:177 in `_log_to_ha()` callback
  - Root cause: MicrosRS232 receive thread calls `_log_to_ha()`, which directly called `async_fire()`
  - Solution: Use `hass.loop.call_soon_threadsafe()` to schedule event on event loop
  - **Impact:** Prevents potential HA crashes and data corruption

### Technical Details
The MicrosRS232 driver runs a dedicated receive thread that monitors the serial port. When it receives data, it calls back to `_log_to_ha()` to notify Home Assistant. However, this callback happens on the worker thread, not the event loop thread.

**Old (UNSAFE):**
```python
self.hass.bus.async_fire("teletask_state_updated", {...})  # Called from worker thread!
```

**New (SAFE):**
```python
self.hass.loop.call_soon_threadsafe(
    self.hass.bus.async_fire,
    "teletask_state_updated",
    {...}
)
```

This ensures the event is fired on the event loop thread, preventing race conditions and crashes.

**Hub Version:** 1.4 → 1.5

## [1.9.12] - 2026-01-20

### Fixed
- **CRITICAL: v1.9.11 missing rebuilt frontend**: Frontend card was not rebuilt/included
  - Bug: v1.9.11 only updated backend files, card still running v1.9.8 code
  - Root cause: Forgot to rebuild and include dist/teletask-test-card.js in commit
  - Solution: Rebuilt frontend with fixed configuration validation logic
  - Card now properly validates and migrates device types
  - **Impact:** Configuration error fixed, card loads correctly

**Test Card Version:** v1.9.12 (rebuilt and included)

**Files Included in v1.9.12:**
- ✅ custom_components/teletask/static/teletask-test-card.js (REBUILT)
- ✅ src/teletask-test-card.ts (version v1.9.12)
- ✅ custom_components/teletask/manifest.json (v1.9.12)
- ✅ CHANGELOG.md

## [1.9.11] - 2026-01-20

### Fixed
- **Synced standalone driver with HA integration**: Fixed TIMED mood support in GUI and CLI
  - Bug: Standalone `teletask/micros_rs232.py` still had old buggy code for mood handling
  - Root cause: v1.9.9 only fixed HA integration, forgot to sync standalone driver
  - Solution: Applied same TIMED mood fix to standalone driver (V06.1 → V06.2)
  - Both versions now use explicit LOCAL/TIMED/GENERAL function code handling
  - **Impact:** TIMED moods now work correctly in GUI and CLI

### Changed
- **GUI: Added TIMED mood support**
  - Updated mood type combobox from ["LOCAL", "GENERAL"] to ["LOCAL", "GENERAL", "TIMED"]
  - GUI version: V06.9 → V06.10
  - **Impact:** Users can now test TIMED moods from GUI

- **CLI: Added TIMED mood support**
  - Updated mood command to accept TIMED type
  - Updated help message: `mood <num> on [local|general|timed]`
  - Updated validation to accept LOCAL/GENERAL/TIMED
  - CLI version: 1.0 → 1.1
  - **Impact:** Users can now test TIMED moods from CLI

### Technical Details
- **Driver V06.2 changes:**
  - Replaced: `func = FUNC_LOCMOOD if mood_type == "LOCAL" else FUNC_GENMOOD`
  - With: Explicit if/elif for LOCAL(8), TIMED(9), GENERAL(10)
  - Added ValueError for invalid mood_type

**All Components Now Synced:**
- ✅ Home Assistant integration (v1.9.11)
- ✅ Standalone driver (V06.2)
- ✅ GUI (V06.10)
- ✅ CLI (1.1)

## [1.9.10] - 2026-01-20

### Fixed
- **CRITICAL: Configuration error after v1.9.9 update**: Completely rewrote config validation
  - Bug: Card failed to load with configuration error after updating
  - Root cause: Config spread operator overwriting corrected device types
  - Solution: Robust config sanitization that filters invalid types and migrates 'mood'
  - Added validation to ensure only valid DeviceType values are used
  - Removed problematic spread operator that caused override issues
  - **Impact:** Card now loads correctly even with old/invalid configurations

### Changed
- **Rebuilt frontend card**: v1.9.9 was backend-only, missing frontend rebuild
  - Test card version now v1.9.10 (synced with backend)

**Test Card Version:** v1.9.10 (updated from v1.9.8)

## [1.9.9] - 2026-01-20

### Fixed
- **CRITICAL: Timed moods now work correctly**: Fixed incorrect function code for timed moods
  - Bug: Timed moods were sent with FUNC_GENMOOD (10) instead of FUNC_TIMEDMOOD (9)
  - Root cause: set_mood() only checked LOCAL vs default to GENERAL, missing TIMED case
  - Solution: Added explicit handling for all three mood types (LOCAL=8, TIMED=9, GENERAL=10)
  - **Impact:** Timed moods now trigger correctly on TeleTask hardware

### Added
- **Mood service debugging**: Added logging to set_mood service handler
  - Logs: "set_mood called: number=X, type=Y, state=Z"
  - Helps diagnose mood control issues in Home Assistant logs
  - **Impact:** Easier troubleshooting when moods don't respond

## [1.9.8] - 2026-01-20

### Fixed
- **Backward compatibility for card configuration**: Fixed configuration error when upgrading from v1.9.5 or earlier
  - Error: Card not loading due to invalid 'mood' device type in old configurations
  - Root cause: Changed DeviceType from 'mood' to 'local_mood', 'general_mood', 'timed_mood'
  - Solution: Automatically migrate old 'mood' type to three new mood types
  - Fixed default_tab undefined type warning
  - **Impact:** Existing card configurations now work without manual YAML edits

**Test Card Version:** v1.9.8 (updated from v1.9.7)

## [1.9.7] - 2026-01-20

### Added
- **Room filter dropdown in test card**: Filter devices by room for easier testing
  - New "Filter by Room" dropdown appears after device type selector
  - Shows "All Rooms" option plus all unique rooms from configured devices
  - Dynamically updates available rooms when device type changes
  - Resets device selection when room filter changes
  - **Impact:** Easier to find and test devices in large installations

### Fixed
- **Duplicate devices in dropdown**: Each device now appears only once
  - Bug: All devices were appearing 3x in the device dropdown
  - Root cause: Multiple entities for same device (e.g., light.relay_5 + switch.relay_5)
  - Solution: Deduplicate by device number instead of entity_id
  - For relays: Prefer light domain over switch when both exist
  - **Impact:** Clean device list with no duplicates

**Test Card Version:** v1.9.7 (updated from v1.9.6)

## [1.9.6] - 2026-01-20

### Fixed
- **Mood controls now working correctly**: Fixed service handler to use actual TeletaskHub methods
  - Error: "'TeletaskHub' object has no attribute 'set_local_mood'"
  - Changed service handler to use hub.trigger_mood() and hub.client.set_mood()
  - Services now call correct backend methods
  - **Impact:** Mood controls (ON/OFF/TOGGLE) now function properly

### Changed
- **Test card UI redesign for moods**: Separated mood types into distinct device types
  - Old: Single "Mood" type with separate mood type selector (LOCAL/GENERAL/TIMED)
  - New: Three separate device types: "Local Mood", "General Mood", "Timed Mood"
  - Removed mood type selector dropdown from control panel
  - Each mood type filters devices by teletask_function (8=LOCAL, 9=GENERAL, 10=TIMED)
  - **Impact:** Cleaner UI, mood type selection now part of device type dropdown

**Test Card Version:** v1.9.6 (updated from v1.9.4)

## [1.9.5] - 2026-01-20

### Fixed
- **Test card config editor error**: Removed non-existent visual editor reference
  - Error: "Visual editor not supported - this._configElement.setConfig is not a function"
  - Removed getConfigElement() method that referenced non-existent 'teletask-test-card-editor'
  - Card now properly shows "YAML configuration only" mode
  - No more confusing error messages when adding card
  - **Impact:** Cleaner UX when adding card to dashboard

**Test Card Version:** v1.9.4 (updated from v1.9.0)

## [1.9.4] - 2026-01-20

### Fixed
- **Service registration async error**: Fixed "Cannot be called from within the event loop"
  - Error: "RuntimeError: Cannot be called from within the event loop" in _register_services
  - Changed `hass.services.register()` to `hass.services.async_register()`
  - Added `has_service()` check to prevent duplicate registration
  - Services now register correctly from async context
  - **Impact:** Integration loads successfully, services work

## [1.9.3] - 2026-01-20

### Fixed
- **Duplicate static route registration error**: Prevented duplicate registration on reload
  - Error: "ValueError: Duplicate 'teletask_card_static', already handled by..."
  - Added check to see if route already exists before registering
  - Prevents error when integration is reloaded or HA restarts
  - **Impact:** Integration now loads successfully on reload/restart without errors

## [1.9.2] - 2026-01-20

### Fixed
- **Frontend resource registration error**: Fixed AttributeError in async_register_static_paths
  - Error: "'dict' object has no attribute 'url_path'"
  - Changed approach: Use aiohttp router.add_static() directly instead of HA HTTP API
  - Static route registered at /teletask_card/teletask-test-card.js
  - Card now loads successfully without errors
  - **Impact:** Test card now accessible in Lovelace

## [1.9.1] - 2026-01-20

### Fixed
- **Blocking I/O warnings in event loop**: Eliminated warnings about blocking file operations
  - Moved TeletaskHub instantiation to executor job in async_setup_entry
  - Config file reads (config.json, devices.json) now happen in thread pool
  - Prevents "Detected blocking call to open" warnings in Home Assistant logs
  - **Impact:** Cleaner logs, better async compliance, no functional change

## [1.9.0] - 2026-01-20

### CRITICAL FIXES - Test Card Now Fully Functional

**Backend (Python) Changes:**
1. **Added teletask_function and teletask_number attributes to ALL entities**
   - light.py: Dimmers (func=2) and Relay Lights (func=1)
   - switch.py: Relay Switches (func=1)
   - button.py: Moods (func=8/9/10 based on type)
   - binary_sensor.py: Flags (func=15) and Inputs (func=21)
   - sensor.py: Sensors (func=20)
   - Also added room attribute for better device display
   - **Fixes:** Test card can now properly filter and display devices

2. **Registered teletask.set_mood and teletask.set_flag services**
   - __init__.py: Added _register_services() function
   - Services accept string states: "ON", "OFF", "TOGGLE"
   - set_mood: parameters number, type (LOCAL/GENERAL), state
   - set_flag: parameters number, state
   - **Fixes:** Mood and flag controls in test card now work

**Frontend (TypeScript) Changes:**
3. **Fixed mood service call parameters**
   - device-control-tab.ts: Changed mood_type → type (correct parameter name)
   - Changed numeric states (255/0/-1) → string states ("ON"/"OFF"/"TOGGLE")
   - **Fixes:** Mood activation now works correctly

4. **Added null checks for entity attributes**
   - device-control-tab.ts: Added `if (!attrs) continue;` check
   - Prevents crashes when entities have missing attributes
   - **Fixes:** Card works reliably even with incomplete entity data

**Test Card Version:** v1.9.0 (was v1.8.1)

### Impact
- **Before v1.9.0:** Test card was completely non-functional - no devices appeared, services didn't exist
- **After v1.9.0:** Test card fully operational - can test relays, dimmers, moods, flags with real-time control

## [1.8.4] - 2026-01-20

### Fixed
- **CRITICAL: unique_id format mismatch for relay switches**: Matter label assignment now works correctly
  - Changed switch.py unique_id from `relay_{num}` to `relay_switch_{num}`
  - Now matches the format expected by Matter label parser in __init__.py
  - Relay switches with `"matter": true` now properly receive the `matterhomes` label

### Improved
- **Error handling in Matter label assignment**: Added try/except around registry updates
  - Prevents one failed entity from breaking the entire label assignment process
  - Logs warnings for individual failures instead of crashing

- **Cross-platform config flow**: Improved default serial port selection
  - Windows: COM6
  - Linux: /dev/ttyUSB0
  - macOS: /dev/tty.usbserial
  - Added duplicate configuration prevention
  - Added proper type hints (FlowResult)
  - Added unique_id check to prevent multiple TeleTask integrations

## [1.8.3] - 2026-01-20

### Fixed
- **Frontend resource registration method**: Fixed AttributeError when loading integration
  - Changed `hass.http.register_static_path()` to `await hass.http.async_register_static_paths()`
  - Changed function to async: `async def _register_frontend_resources()`
  - Updated method signature from singular to plural with dict list format
  - Integration now loads successfully without errors

## [1.8.2] - 2026-01-19

### Fixed
- **Critical import error**: Fixed "No module named 'teletask.micros_rs232'" error
  - Changed all absolute imports (`from teletask.xxx`) to relative imports (`from .teletask.xxx`)
  - Fixed in: teletask_hub.py, light.py, switch.py, binary_sensor.py, button.py, number.py, sensor.py
  - Integration now loads correctly in Home Assistant

## [1.8.1] - 2026-01-19

### Fixed
- **Frontend resource registration**: Fixed TeleTask Test Card not appearing in card picker
  - Changed from manifest.json `frontend` section to programmatic registration using `add_extra_js_url()`
  - Added `frontend` dependency to manifest.json
  - Card now properly registers and appears in Lovelace card picker
  - Fixed static path from `/hacsfiles/...` to `/teletask_static/...`

## [1.8.0] - 2026-01-19

### Added
- **TeleTask Test Card**: New custom Lovelace card for device testing and event monitoring
  - **Device Control Tab**: Test relays, dimmers, moods, and flags directly from the dashboard
    - Relay/Flag controls: ON, OFF, TOGGLE, Get Status
    - Dimmer controls: Brightness slider (0-255), Set, Toggle, Get Status
    - Mood controls: Type selector (LOCAL/GENERAL/TIMED), ON, OFF, TOGGLE, Get Status
    - Auto-detection of all configured TeleTask devices
  - **Event Monitor Tab**: Real-time log of TeleTask communication events
    - Live event display with timestamp, type, function, device number, and state
    - Auto-scroll to latest events (toggleable)
    - Clear log functionality
    - Connection status indicator
  - Modern responsive design matching Home Assistant styling
  - Automatic registration via manifest.json (no manual resource loading needed)
  - TypeScript implementation using Lit framework

### Changed
- Updated manifest.json to v1.8.0 with frontend resource registration
- Updated __init__.py to register static path for card resources
- Added frontend build configuration (package.json, rollup, tsconfig)

### Developer Notes
- Frontend source in `src/` directory (TypeScript/Lit)
- Build with `npm run build` to generate `dist/teletask-test-card.js`
- Copy compiled JS to `custom_components/teletask/static/` for distribution

## [1.7.0] - 2026-01-19

### Added
- **Button platform for mood control**: Moods (Local, General, Timed) are now exposed as button entities in Home Assistant
  - Press to trigger mood activation
  - Respects `ha` flag in devices.json configuration
  - Supports Matter bridge via `matter` flag
  - Automatic room/area assignment based on mood configuration
  - Custom icons with sensible defaults (lightbulb-group)
  - Extra state attributes: `mood_type` and `matter_enabled`

### Fixed
- **Number entities now respect ha flag**: Dimmer number entities were previously created for all dimmers regardless of the `ha` setting in devices.json. Now only dimmers with `ha: true` are exposed as number entities.

### Changed
- Extended Matter label support to include mood entities
- Updated `_should_have_matter_label()` to handle mood_local and mood_general entity types

## [1.6.0] - Previous Release

### Added
- Automatic `matterhomes` label assignment for Matter-enabled entities
- Matter bridge integration support
- Enhanced device configuration with `ha` and `matter` flags

## [1.5.0] - Previous Release

### Added
- Binary sensor support for inputs
- Sensor support for analog values (temperature, humidity, etc.)
- Room-based area assignment

## [1.4.0] - Initial HACS Release

### Added
- Initial Home Assistant custom integration
- Support for relays (light/switch)
- Support for dimmers (light with brightness)
- Support for flags (binary sensor)
- RS232 and TCP/IP connection support
- JSON-based device configuration
