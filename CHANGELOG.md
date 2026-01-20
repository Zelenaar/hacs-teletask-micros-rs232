# Changelog

All notable changes to this project will be documented in this file.

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
