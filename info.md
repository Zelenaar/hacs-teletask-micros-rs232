# TeleTask MICROS Integration

Home Assistant integration for **TeleTask MICROS** home automation systems.

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
- Serial-over-IP (TCP)

## Configuration

After installation, create a `devices.json` file with your TeleTask device configuration. See the [documentation](https://github.com/Zelenaar/hacs-teletask-micros-rs232#configuration) for details.

## Requirements

- Home Assistant 2023.1.0+
- TeleTask MICROS with RS232 interface
