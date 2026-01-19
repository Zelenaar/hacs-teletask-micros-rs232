# TeleTask Home Assistant Integration - Installation Guide

This guide will help you install and configure the TeleTask integration for Home Assistant, including Matter bridge setup for exposing your devices to third-party apps like Google Home and Aqara Home.

**Table of Contents:**
1. [Prerequisites](#1-prerequisites)
2. [Install the TeleTask Integration](#2-install-the-teletask-integration)
3. [Create Configuration Files](#3-create-configuration-files)
4. [Configure Your Devices](#4-configure-your-devices)
5. [Verify Devices in Home Assistant](#5-verify-devices-in-home-assistant)
6. [Install Matter Server Add-on](#6-install-matter-server-add-on)
7. [Expose Devices via Matter](#7-expose-devices-via-matter)
8. [Connect to Third-Party Apps](#8-connect-to-third-party-apps)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

Before you begin, make sure you have:

- **Home Assistant** installed and running (HAOS, Docker, or Supervised installation)
- **TeleTask MICROS** central unit with RS232 interface
- **Serial connection** to your MICROS:
  - Direct RS232 cable, OR
  - USB-to-RS232 adapter, OR
  - Serial-over-IP device (like a Moxa NPort) - **recommended**
- **Network access** to your Home Assistant instance

### What You'll Need to Know

| Information | Example | Where to Find It |
|-------------|---------|------------------|
| Serial port or IP address | `COM3` or `socket://192.168.1.100:4001` | Your serial adapter settings |
| TeleTask device numbers | Relay 1, Dimmer 5, etc. | TeleTask PROSOFT configuration |

---

## 2. Install the TeleTask Integration

### Option A: Install via HACS (Recommended)

HACS (Home Assistant Community Store) is the easiest way to install and keep the integration updated.

**Step 2.1: Install HACS (if not already installed)**

If you don't have HACS yet, follow the [HACS installation guide](https://hacs.xyz/docs/setup/download).

**Step 2.2: Add the Custom Repository**

1. Open Home Assistant
2. Go to **HACS** in the sidebar
3. Click the three dots menu (top right) → **Custom repositories**
4. Add repository URL: `https://github.com/Zelenaar/hacs-teletask-micros-rs232`
5. Select category: **Integration**
6. Click **Add**

**Step 2.3: Download the Integration**

1. In HACS, search for "**TeleTask**"
2. Click on "TeleTask MICROS"
3. Click **Download**
4. **Restart Home Assistant**: Go to **Settings** > **System** > **Restart**

### Option B: Manual Installation

If you prefer not to use HACS, you can install manually.

**Step 2.1: Access Home Assistant Files**

You need to copy files to your Home Assistant configuration folder. There are several ways to do this:

- **File Editor Add-on**: Install from Add-on Store, use the web UI
- **Samba Share Add-on**: Access `\\homeassistant\config` from your PC
- **SSH**: Use the Terminal & SSH add-on

**Step 2.2: Download and Copy Files**

1. Download the latest release from [GitHub](https://github.com/Zelenaar/hacs-teletask-micros-rs232/releases)
2. Extract the `custom_components/teletask` folder
3. Copy it to your Home Assistant `config/custom_components/` directory

Your structure should look like:
```
config/
├── custom_components/
│   └── teletask/
│       ├── __init__.py
│       ├── manifest.json
│       ├── light.py
│       ├── switch.py
│       └── ... (other files)
```

**Step 2.3: Restart Home Assistant**

Go to **Settings** > **System** > **Restart**

---

## 3. Create Configuration Files

The integration requires two configuration files in a dedicated `teletask` folder.

### 3.1 Create the Folder Structure

Create the following folder structure in your Home Assistant config directory:

```
config/
└── teletask/
    ├── config.json      # Connection settings
    └── devices.json     # Device configuration
```

### 3.2 Create `teletask/config.json` (Connection Settings)

Create a file at `/config/teletask/config.json` with your connection settings.

**For TCP/IP connection (recommended for Serial-over-IP devices like Moxa NPort):**

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
| Connection Type | Port Format |
|-----------------|-------------|
| TCP/IP (Moxa NPort) | `socket://192.168.1.100:4001` |
| Windows serial | `COM6` |
| Linux serial | `/dev/ttyUSB0` |

---

## 4. Configure Your Devices

### Step 4.1: Create devices.json

The `devices.json` file defines which TeleTask devices appear in Home Assistant.

Create `/config/teletask/devices.json`:

```json
{
  "_comment": "TeleTask device configuration",
  "_version": "1.4",
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

### Step 4.2: Understanding the Configuration

**Field Reference:**

| Field | Required | Description |
|-------|----------|-------------|
| `num` | Yes | TeleTask device number (from PROSOFT) |
| `name` | Yes | Friendly name shown in HA |
| `room` | No | Room name for automatic area assignment |
| `icon` | No | MDI icon name (without `mdi:` prefix) |
| `type` | Depends | See below |
| `ha` | No | `true` = show in HA, `false` = hide (default: true) |
| `matter` | No | `true` = expose via Matter (default: false) |

**Type Field by Device Category:**

| Category | Type Options | Effect |
|----------|--------------|--------|
| Relays | `light` | Creates a light entity (for Matter compatibility) |
| Relays | `switch` or empty | Creates a switch entity |
| Dimmers | (ignored) | Always creates a dimmable light |
| Moods | `LOCAL`, `GENERAL`, or `TIMED` | Determines mood type |
| Inputs | `motion`, `door`, `window`, `button`, `smoke` | Sets HA device class |
| Sensors | `temperature`, `humidity`, `illuminance` | Sets HA device class |

**Icons:**
Find icons at [Material Design Icons](https://pictogrammers.com/library/mdi/). Use just the name, e.g., `ceiling-light` not `mdi:ceiling-light`.

### Step 4.3: Save and Restart

After editing `devices.json`:
1. Save the file
2. Restart Home Assistant: **Settings** > **System** > **Restart**

---

## 5. Verify Devices in Home Assistant

### Step 5.1: Add the Integration

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "**TeleTask**"
4. Enter your serial port (e.g., `COM6` or `socket://192.168.1.100:4001`)
5. Click **Submit**

### Step 5.2: Check the Device

1. After adding, click on the **TeleTask** integration
2. You should see **1 device** with multiple entities
3. Click on the device to see all entities

### Step 5.3: Test Entity Control

1. Go to **Settings** > **Devices & Services** > **Entities**
2. Find one of your TeleTask entities (e.g., `light.living_room_ceiling_light`)
3. Click on it and try toggling it on/off
4. Check that the physical device responds

### Step 5.4: Check Entity Attributes

1. Go to **Developer Tools** > **States**
2. Find a TeleTask entity
3. Look at the **Attributes** section
4. You should see `matter_enabled: true` or `matter_enabled: false`

---

## 6. Matter Bridge Setup

Matter allows your TeleTask devices to be controlled by Google Home, Apple Home, Amazon Alexa, and other Matter-compatible apps.

### Automatic Label Assignment

The TeleTask integration automatically assigns the `matterhomes` label to all entities with `"matter": true` in your devices.json. This makes filtering easy when configuring Matter bridges.

You can verify this in Home Assistant:
1. Go to **Settings** > **Labels**
2. You should see "**Matter Homes**" with a home-automation icon
3. Click on it to see all labeled entities

---

### Option A: Home Assistant Matter Hub (Recommended)

The [Home Assistant Matter Hub](https://github.com/t0bst4r/home-assistant-matter-hub) by t0bst4r is an excellent way to expose HA entities to Matter. It supports filtering by labels and provides a clean web interface.

#### Step 6.1: Add the Repository

1. Go to **Settings** > **Add-ons**
2. Click **Add-on Store**
3. Click the three dots menu (top right) > **Repositories**
4. Add: `https://github.com/t0bst4r/home-assistant-matter-hub`
5. Click **Add** and **Close**

#### Step 6.2: Install the Add-on

1. Refresh the Add-on Store page
2. Scroll down to find **Home Assistant Matter Hub** (in the new repository section)
3. Click on it, then click **Install**
4. Wait for installation to complete
5. Toggle **Start on boot** to ON
6. Toggle **Watchdog** to ON (recommended)
7. Click **Start**

#### Step 6.3: Configure Entity Filter

1. Click **Open Web UI**
2. Create a new Matter bridge
3. In the entity filter settings, add the label filter: `matterhomes`
4. Save the configuration

This filter ensures only TeleTask entities with `matter: true` are exposed to Matter.

#### Step 6.4: Get Pairing Code

1. In the Web UI, look for the **QR code** or **pairing code** for your bridge
2. Use this code to add the bridge to Google Home, Apple Home, etc.

---

### Option B: Matterbridge Add-on

The [Matterbridge add-on](https://github.com/Luligu/matterbridge-home-assistant-addon) by Luligu is another option for exposing HA entities to Matter.

#### Step 6.1: Add the Repository

1. Go to **Settings** > **Add-ons**
2. Click **Add-on Store**
3. Click the three dots menu (top right) > **Repositories**
4. Add: `https://github.com/Luligu/matterbridge-home-assistant-addon`
5. Click **Add** and **Close**

#### Step 6.2: Install Matterbridge

1. Refresh the Add-on Store page
2. Scroll down to find **Matterbridge** (in the new repository section)
3. Click on it, then click **Install**
4. Wait for installation to complete
5. Toggle **Start on boot** to ON
6. Toggle **Watchdog** to ON (recommended)
7. Click **Start**

#### Step 6.3: Configure Entity Filter

1. Click **Open Web UI** (or go to the Matterbridge URL shown)
2. In the Matterbridge interface, go to **Home Assistant** plugin settings
3. Set the **Entity filter** to: `label:matterhomes`
4. Save the configuration

#### Step 6.4: Get Pairing Code

1. In the Matterbridge Web UI, look for the **QR code** or **pairing code**
2. Use this code to add the bridge to Google Home, Apple Home, etc.

---

### Option C: Official Matter Server Add-on

The official Matter Server is more feature-rich but requires more setup.

#### Step 6.1: Install the Add-on

1. Go to **Settings** > **Add-ons**
2. Click **Add-on Store**
3. Search for "**Matter Server**"
4. Click on it, then click **Install**
5. Wait for installation to complete
6. Toggle **Start on boot** to ON
7. Click **Start**

#### Step 6.2: Enable Matter Integration

1. Go to **Settings** > **Devices & Services**
2. You should see "**Matter**" discovered automatically
3. Click **Configure** and follow the prompts

#### Step 6.3: Expose Entities

1. Go to **Settings** > **Devices & Services** > **Matter** > **Configure**
2. Click **Expose entities to Matter**
3. Filter by the `matterhomes` label to find your TeleTask entities
4. Select the entities you want to expose

---

## 7. Entity Type Compatibility

Not all entity types are fully supported by Matter. Here's what works:

| HA Entity Type | Matter Support | Notes |
|----------------|----------------|-------|
| `light` | Yes | Full support including brightness |
| `switch` | Yes | On/off only |
| `binary_sensor` | Limited | Some device classes only |
| `sensor` | Limited | Temperature, humidity |
| `climate` | Yes | Thermostats |

**Important:** Relays configured as `"type": "light"` will appear as lights in Matter, which is better supported than switches in most Matter apps.

---

## 8. Connect to Third-Party Apps

Now you can add your Home Assistant (as a Matter bridge) to other smart home apps.

### 8.1 General Process

1. In Home Assistant, go to **Settings** > **Devices & Services** > **Matter**
2. Click **Configure**
3. Click **Commission** or look for a **QR code** / **pairing code**
4. Use this code in your third-party app

### 8.2 Google Home

**Requirements:**
- Google Home app on your phone
- Google Nest Hub or other Google Home device

**Steps:**
1. Open the **Google Home** app
2. Tap **+** (Add)
3. Select **Set up device**
4. Choose **New device**
5. Select **Matter-enabled device**
6. Scan the QR code from Home Assistant, or enter the pairing code manually
7. Follow the prompts to complete setup
8. Your TeleTask devices will appear in Google Home

### 8.3 Aqara Home

**Requirements:**
- Aqara Home app
- Aqara Hub M3 or other Matter-compatible Aqara hub

**Steps:**
1. Open the **Aqara Home** app
2. Go to **Settings** > **Add accessory**
3. Select **Matter device**
4. Scan the QR code from Home Assistant
5. Wait for pairing to complete
6. Your devices will appear in Aqara Home

### 8.4 Apple Home (HomeKit)

**Requirements:**
- Apple Home app on iPhone/iPad
- HomePod, HomePod mini, or Apple TV as a home hub

**Steps:**
1. Open the **Home** app on your iPhone/iPad
2. Tap **+** > **Add Accessory**
3. Scan the Matter QR code
4. Follow the prompts to add the bridge
5. Assign rooms to each device

### 8.5 Amazon Alexa

**Requirements:**
- Alexa app
- Echo device (4th gen or newer) with Matter support

**Steps:**
1. Open the **Alexa** app
2. Go to **Devices** > **+** > **Add Device**
3. Select **Matter**
4. Scan the QR code or enter the setup code
5. Complete the setup process

---

## 9. Troubleshooting

### Integration Not Found

**Problem:** "TeleTask" doesn't appear when adding integrations.

**Solution:**
1. If using HACS, verify the integration was downloaded
2. Check that files exist in `config/custom_components/teletask/`
3. Check Home Assistant logs: **Settings** > **System** > **Logs**
4. Look for errors mentioning "teletask"
5. Restart Home Assistant

### Config File Not Found

**Problem:** Error about missing config.json

**Solution:**
1. Create the `teletask` folder in your Home Assistant config directory
2. Create `config.json` inside the `teletask` folder using the template from Section 3.2
3. Ensure the file is valid JSON (use a JSON validator)

### Cannot Connect to MICROS

**Problem:** Integration fails to connect.

**Solutions:**
1. Verify `config.json` has the correct port/IP settings
2. Check IP address and port for TCP connections
3. Check firewall settings
4. Verify the serial port is not in use by another application
5. Test network connectivity to your serial-over-IP device

### Devices Not Appearing

**Problem:** Integration connects but no entities appear.

**Solutions:**
1. Check `teletask/devices.json` exists
2. Validate JSON syntax (use a JSON validator)
3. Verify device numbers match your TeleTask configuration
4. Check that `"ha": true` is set for devices you want to see
5. Restart Home Assistant after editing devices.json

### Matter Pairing Fails

**Problem:** Cannot pair with Google Home or other apps.

**Solutions:**
1. Make sure Matter Server add-on is running
2. Ensure your phone is on the same network as Home Assistant
3. Check that the entities are exposed in Matter settings
4. Try restarting the Matter Server add-on
5. Check Matter Server logs for errors

### Entities Not Responding

**Problem:** Entities appear but don't control devices.

**Solutions:**
1. Check the connection in HA logs
2. Verify device numbers are correct
3. Check that the TeleTask MICROS is powered on
4. Verify serial/network connection is stable

### Matter Devices Show "Unavailable" in Third-Party Apps

**Problem:** Devices pair but show offline.

**Solutions:**
1. Check Home Assistant is running
2. Verify Matter Server add-on is running
3. Ensure network connectivity between all devices
4. Try removing and re-adding the Matter bridge

---

## Appendix: File Structure

After complete setup, your config folder should look like:

```
config/
├── teletask/                        # TeleTask configuration folder
│   ├── config.json                  # Connection settings
│   └── devices.json                 # Device configuration
└── custom_components/
    └── teletask/                    # Integration (installed by HACS)
        ├── __init__.py
        ├── manifest.json
        ├── light.py
        ├── switch.py
        ├── binary_sensor.py
        ├── sensor.py
        ├── teletask_hub.py
        └── teletask/
            ├── micros_rs232.py
            ├── protocol.py
            └── device_config.py
```

---

## Getting Help

- **GitHub Issues:** https://github.com/Zelenaar/hacs-teletask-micros-rs232/issues
- **Home Assistant Community:** https://community.home-assistant.io/
- **Matter Documentation:** https://www.home-assistant.io/integrations/matter/
- **TeleTask Support:** Contact your TeleTask installer

---

*Document Version: 2.0*
*Last Updated: January 2026*
