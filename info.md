# TeleTask MICROS Integration

Home Assistant integration for **TeleTask MICROS** home automation systems via RS232 or TCP/IP.

## Features

- **Relays** - Control as lights or switches
- **Dimmers** - Full brightness control (0-255)
- **Moods** - Activate Local, General, and Timed moods
- **Flags & Inputs** - Monitor as binary sensors
- **Sensors** - Temperature, humidity, illuminance
- **Matter Support** - Expose devices via Matter bridge

## Connection

Connects to TeleTask MICROS via:
- RS232 serial port
- USB-to-RS232 adapter
- Serial-over-IP (TCP) - e.g., `socket://192.168.1.100:4001`

## Configuration

After installation, create two configuration files:

1. **`config.json`** - Connection settings (serial port or TCP)
2. **`packages/teletask/devices.json`** - Device definitions

See the [full documentation](https://github.com/Zelenaar/hacs-teletask-micros-rs232#configuration) for details.

## Requirements

- Home Assistant 2023.1.0+
- TeleTask MICROS with RS232 interface
