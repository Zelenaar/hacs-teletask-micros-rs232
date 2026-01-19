# Changelog

All notable changes to this project will be documented in this file.

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
