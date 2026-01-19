# Changelog

All notable changes to this project will be documented in this file.

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
