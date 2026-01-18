# TeleTask MICROS Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Zelenaar/hacs-teletask-micros-rs232.svg)](https://github.com/Zelenaar/hacs-teletask-micros-rs232/releases)
[![License](https://img.shields.io/github/license/Zelenaar/hacs-teletask-micros-rs232.svg)](LICENSE)

Home Assistant custom integration for **TeleTask MICROS** home automation systems via RS232/TCP.

## Features

- Control TeleTask relays (as lights or switches)
- Control TeleTask dimmers (with brightness)
- Activate moods (Local, General, Timed)
- Monitor flags and inputs as binary sensors
- Read sensor values (temperature, humidity, etc.)
- Real-time state updates via event monitoring
- Matter bridge support via `matter_enabled` attribute

## Supported Devices

| Device Type | Home Assistant Entity | Features |
|-------------|----------------------|----------|
| Relays | `light` or `switch` | On/Off control |
| Dimmers | `light` | Brightness 0-255 |
| Moods | `button` | Activate local/general/timed moods |
| Flags | `binary_sensor` | State monitoring |
| Inputs | `binary_sensor` | Motion, door, window sensors |
| Sensors | `sensor` | Temperature, humidity, illuminance |

## Requirements

- Home Assistant 2023.1.0 or newer
- TeleTask MICROS central unit with RS232 interface
- Connection via:
  - Direct RS232 cable
  - USB-to-RS232 adapter
  - Serial-over-IP device (e.g., Moxa NPort)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu (top right) → **Custom repositories**
3. Add this repository URL: `https://github.com/Zelenaar/hacs-teletask-micros-rs232`
4. Select category: **Integration**
5. Click **Add**
6. Search for "TeleTask" in HACS
7. Click **Download**
8. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Extract and copy the `custom_components/teletask` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Step 1: Create devices.json

Create a `devices.json` file in `config/packages/teletask/` with your device configuration:

```json
{
  "relays": [
    {
      "num": 1,
      "name": "Ceiling Light",
      "room": "Living Room",
      "icon": "ceiling-light",
      "type": "light",
      "ha": true,
      "matter": true
    }
  ],
  "dimmers": [
    {
      "num": 1,
      "name": "Wall Dimmer",
      "room": "Living Room",
      "icon": "lightbulb-on",
      "type": "",
      "ha": true,
      "matter": true
    }
  ],
  "moods": [
    {
      "num": 1,
      "name": "All Off",
      "room": "",
      "icon": "lightbulb-group-off",
      "type": "GENERAL",
      "ha": true,
      "matter": false
    }
  ],
  "flags": [],
  "inputs": [],
  "sensors": []
}
```

### Step 2: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **TeleTask**
4. Enter your connection details:
   - **Host**: IP address or hostname (e.g., `192.168.1.100`)
   - **Port**: TCP port (e.g., `4001`)

### Configuration Options

| Field | Description |
|-------|-------------|
| `num` | TeleTask device number (from PROSOFT) |
| `name` | Friendly name shown in HA |
| `room` | Room name for automatic area assignment |
| `icon` | MDI icon name (without `mdi:` prefix) |
| `type` | Device type: `light`/`switch` for relays, `LOCAL`/`GENERAL`/`TIMED` for moods |
| `ha` | `true` to expose in Home Assistant |
| `matter` | `true` to expose via Matter bridge |

## Matter Bridge Support

Devices with `"matter": true` will have a `matter_enabled` attribute set to `true`. Use this to filter which entities to expose via the Home Assistant Matter integration:

1. Install the **Matter Server** add-on
2. Go to **Settings** → **Devices & Services** → **Matter** → **Configure**
3. Select entities where `matter_enabled: true`

## Extracting Device Configuration

Use the included GUI tool to extract device configuration from PROSOFT NBT files:

1. Run `gui/PHAeletaskV2_testGUI.py`
2. Go to the **Extract** tab
3. Select your `.NBT` file
4. Click **Extract & Preview**
5. Save the generated `devices.json`

## Troubleshooting

### Integration not found
- Verify files are in `config/custom_components/teletask/`
- Check Home Assistant logs for errors
- Restart Home Assistant

### Cannot connect to MICROS
- Verify IP address and port
- Check firewall settings
- Test with the CLI tool: `python teletask_cli.py -i`

### Devices not appearing
- Check `devices.json` syntax
- Verify `"ha": true` is set
- Restart Home Assistant after changes

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Developed for TeleTask MICROS home automation systems commonly used in Belgium and the Netherlands.
