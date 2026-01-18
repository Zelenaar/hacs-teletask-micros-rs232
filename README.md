# TeleTask MICROS Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Zelenaar/hacs-teletask-micros-rs232.svg)](https://github.com/Zelenaar/hacs-teletask-micros-rs232/releases)
[![License](https://img.shields.io/github/license/Zelenaar/hacs-teletask-micros-rs232.svg)](LICENSE)

Home Assistant custom integration for **TeleTask MICROS** home automation systems via RS232 or TCP/IP.

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
  - Serial-over-IP device (e.g., Moxa NPort) - recommended

## Installation

### Step 1: Install via HACS

1. Open HACS in Home Assistant
2. Click the three dots menu (top right) → **Custom repositories**
3. Add repository URL: `https://github.com/Zelenaar/hacs-teletask-micros-rs232`
4. Select category: **Integration**
5. Click **Add**
6. Search for "TeleTask" in HACS
7. Click **Download**
8. **Restart Home Assistant**

### Step 2: Create Configuration Files

Create a `teletask` folder in your Home Assistant config directory with two configuration files.

#### 2.1 Create the folder structure

```
config/
└── teletask/
    ├── config.json      # Connection settings
    └── devices.json     # Device configuration
```

#### 2.2 Create `teletask/config.json` (Connection Settings)

Create a file at `/config/teletask/config.json` with your connection settings:

**For TCP/IP connection (recommended):**
```json
{
  "serial": {
    "port": "socket://192.168.1.100:4001",
    "baudrate": 19200,
    "timeout": 1.0
  },
  "reliability": {
    "retries": 3,
    "confirm_timeout_ms": 800,
    "ack_timeout_ms": 300,
    "retry_delay_ms": 250,
    "post_send_gap_ms": 140,
    "pre_send_flush": false
  }
}
```

**For direct serial connection:**
```json
{
  "serial": {
    "port": "COM6",
    "baudrate": 19200,
    "timeout": 1.0
  },
  "reliability": {
    "retries": 3,
    "confirm_timeout_ms": 800,
    "ack_timeout_ms": 300,
    "retry_delay_ms": 250,
    "post_send_gap_ms": 140,
    "pre_send_flush": false
  }
}
```

**Port examples:**
- `socket://192.168.1.100:4001` - TCP/IP via Moxa NPort or similar
- `COM6` - Windows serial port
- `/dev/ttyUSB0` - Linux serial port

#### 2.3 Create `teletask/devices.json` (Device Configuration)

Create the file at `/config/teletask/devices.json`:

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
    },
    {
      "num": 2,
      "name": "Wall Outlet",
      "room": "Living Room",
      "icon": "power-socket-eu",
      "type": "switch",
      "ha": true,
      "matter": false
    }
  ],
  "dimmers": [
    {
      "num": 1,
      "name": "Dining Light",
      "room": "Dining Room",
      "icon": "chandelier",
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

### Step 3: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **TeleTask**
4. Enter a serial port value (this can match your config.json or be a placeholder)
5. Click **Submit**

### Configuration Field Reference

| Field | Description |
|-------|-------------|
| `num` | TeleTask device number (from PROSOFT configuration) |
| `name` | Friendly name shown in Home Assistant |
| `room` | Room name for automatic area assignment |
| `icon` | MDI icon name without `mdi:` prefix (see [MDI icons](https://pictogrammers.com/library/mdi/)) |
| `type` | `light` or `switch` for relays; `LOCAL`, `GENERAL`, or `TIMED` for moods |
| `ha` | `true` to expose in Home Assistant, `false` to hide |
| `matter` | `true` to expose via Matter bridge (requires `ha: true`) |

## Matter Bridge Support

Devices with `"matter": true` will automatically receive the `matterhomes` label in Home Assistant. This makes it easy to expose them via Matter using either the official Matter Server or the Matterbridge add-on.

### Option A: Home Assistant Matter Hub (Recommended)

The [Home Assistant Matter Hub](https://github.com/t0bst4r/home-assistant-matter-hub) by t0bst4r exposes HA entities as Matter devices. It supports filtering by labels.

**Installation:**

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the three dots menu → **Repositories**
3. Add: `https://github.com/t0bst4r/home-assistant-matter-hub`
4. Find **Home Assistant Matter Hub** in the store and click **Install**
5. Start the add-on and open the **Web UI**

**Configure to use the matterhomes label:**

1. In the Web UI, create a new bridge
2. Set the entity filter to include label: `matterhomes`
3. Only TeleTask entities with `matter: true` will be exposed

### Option B: Matterbridge Add-on

The [Matterbridge add-on](https://github.com/Luligu/matterbridge-home-assistant-addon) by Luligu is another option for exposing HA entities to Matter.

**Installation:**

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the three dots menu → **Repositories**
3. Add: `https://github.com/Luligu/matterbridge-home-assistant-addon`
4. Find **Matterbridge** in the store and click **Install**
5. Start the add-on and open the **Web UI**

**Configure to use the matterhomes label:**

1. In the Matterbridge Web UI, go to **Home Assistant** plugin settings
2. Set the entity filter to: `label:matterhomes`
3. Only TeleTask entities with `matter: true` will be exposed

### Option C: Official Matter Server

1. Install the **Matter Server** add-on from the Add-on Store
2. Go to **Settings** → **Devices & Services** → **Matter** → **Configure**
3. Select entities to expose (look for the `matterhomes` label)

## File Structure

After setup, your config folder should look like:

```
config/
├── teletask/
│   ├── config.json             # Connection settings
│   └── devices.json            # Device configuration
└── custom_components/
    └── teletask/               # Integration (installed by HACS)
```

## Troubleshooting

### Integration not found
- Verify HACS downloaded the integration
- Check that files exist in `config/custom_components/teletask/`
- Restart Home Assistant

### Cannot connect to MICROS
- Verify `teletask/config.json` exists in your config folder
- Check IP address/port or serial port settings
- Verify firewall allows the connection
- Test network connectivity to your serial-over-IP device

### Devices not appearing
- Verify `teletask/devices.json` exists and has valid JSON
- Check that `"ha": true` is set for devices you want to see
- Restart Home Assistant after changing devices.json

### Config file not found error
- Create the `teletask` folder in your Home Assistant config directory
- Create both `config.json` and `devices.json` inside the `teletask` folder
- Ensure the files contain valid JSON (use a JSON validator)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Developed for TeleTask MICROS home automation systems commonly used in Belgium and the Netherlands.

## Support

- [Report issues](https://github.com/Zelenaar/hacs-teletask-micros-rs232/issues)
- [TeleTask website](https://www.teletask.be/)
