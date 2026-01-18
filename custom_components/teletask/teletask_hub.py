
#################################################################################################
# File:    teletask_hub.py
# Version: 1.4 - Added get_matter_enabled_devices() for label assignment
#################################################################################################

import logging
import os
from typing import Dict, Any, Optional, List

from homeassistant.core import HomeAssistant

from .teletask.micros_rs232 import MicrosRS232
from .teletask.protocol import (
    FUNC_RELAY, FUNC_DIMMER, FUNC_FLAG,
    FUNC_LOCMOOD, FUNC_GENMOOD, FUNC_SENSOR
)
from .teletask.device_config import load_device_config_safe, DeviceConfig, DeviceInfo, SensorInfo

_LOGGER = logging.getLogger(__name__)

# Config paths relative to HA config directory
TELETASK_CONFIG_DIR = "teletask"
CONNECTION_CONFIG_FILE = "config.json"
DEVICES_CONFIG_FILE = "devices.json"


class TeletaskHub:
    """Home Assistant bridge around MicrosRS232 driver."""

    def __init__(self, hass: HomeAssistant, data: Dict[str, Any]) -> None:
        """
        Initialize the TeleTask hub.

        Args:
            hass: Home Assistant instance.
            data: Configuration data from config entry.
        """
        self.hass = hass
        self.serial_port = data.get("serial_port", "")

        # Build config paths relative to HA config directory
        # All TeleTask config files are in config/teletask/
        config_dir = hass.config.path()
        teletask_dir = os.path.join(config_dir, TELETASK_CONFIG_DIR)
        config_file = os.path.join(teletask_dir, CONNECTION_CONFIG_FILE)
        devices_file = os.path.join(teletask_dir, DEVICES_CONFIG_FILE)

        self.client = MicrosRS232(
            config_path=config_file,
            log_callback=self._log_to_ha
        )

        # Load device configuration
        self.device_config: Optional[DeviceConfig] = load_device_config_safe(devices_file)
        if self.device_config:
            _LOGGER.info(
                "Loaded device config: %d relays, %d dimmers, %d flags, %d moods",
                len(self.device_config.relays),
                len(self.device_config.dimmers),
                len(self.device_config.flags),
                len(self.device_config.local_moods) + len(self.device_config.general_moods)
            )
        else:
            _LOGGER.warning("No device config found at %s/%s, using defaults", TELETASK_CONFIG_DIR, DEVICES_CONFIG_FILE)

        # Latest states for HA entities
        self.relay_state: Dict[int, bool] = {}
        self.dimmer_state: Dict[int, int] = {}
        self.flag_state: Dict[int, bool] = {}
        self.input_state: Dict[int, bool] = {}
        self.sensor_state: Dict[int, float] = {}

        # Running flag
        self.running = False

    def get_configured_relays(self) -> List[DeviceInfo]:
        """Get list of configured relays, or default range if no config."""
        if self.device_config and self.device_config.relays:
            return self.device_config.get_all_relays()
        # Default: create basic info for relays 1-64
        return [DeviceInfo(num=i, name=f"Relay {i}") for i in range(1, 65)]

    def get_configured_dimmers(self) -> List[DeviceInfo]:
        """Get list of configured dimmers, or default range if no config."""
        if self.device_config and self.device_config.dimmers:
            return self.device_config.get_all_dimmers()
        # Default: create basic info for dimmers 1-32
        return [DeviceInfo(num=i, name=f"Dimmer {i}") for i in range(1, 33)]

    def get_configured_flags(self) -> List[DeviceInfo]:
        """Get list of configured flags, or default range if no config."""
        if self.device_config and self.device_config.flags:
            return self.device_config.get_all_flags()
        # Default: create basic info for flags 1-32
        return [DeviceInfo(num=i, name=f"Flag {i}") for i in range(1, 33)]

    def get_configured_inputs(self) -> List[DeviceInfo]:
        """Get list of configured inputs (digital inputs / binary sensors)."""
        if self.device_config and self.device_config.inputs:
            return self.device_config.get_all_inputs()
        # Default: empty list (inputs must be explicitly configured)
        return []

    def get_configured_sensors(self) -> List[SensorInfo]:
        """Get list of configured sensors (analog sensors)."""
        if self.device_config and self.device_config.sensors:
            return self.device_config.get_all_sensors()
        # Default: empty list (sensors must be explicitly configured)
        return []

    def _log_to_ha(self, msg: str) -> None:
        """
        Forward driver logs to HA log and parse state updates.

        Args:
            msg: Log message from the driver.
        """
        _LOGGER.debug("[TeleTask] %s", msg)

        # Parse state change events (events the driver already parsed)
        if "RX:" not in msg:
            return

        # Example: "HH:MM:SS  RX: 02 07 08 01 03 FF xx"
        try:
            parts = msg.split("  RX:")
            if len(parts) < 2:
                return
            hex_str = parts[1].strip()
            b = [int(x, 16) for x in hex_str.split()]
        except (ValueError, IndexError) as e:
            _LOGGER.warning("Failed to parse RX message: %s - %s", msg, e)
            return

        if len(b) < 6:
            return

        cmd = b[2]
        func = b[3]
        num = b[4]
        st = b[5]

        # EVENT = CMD 8
        if cmd == 8:
            if func == FUNC_RELAY:
                self.relay_state[num] = (st == 255)

            elif func == FUNC_DIMMER:
                self.dimmer_state[num] = st

            elif func == FUNC_FLAG:
                self.flag_state[num] = (st == 255)

            elif func == FUNC_SENSOR:
                # Sensor values are typically raw ADC or scaled values
                self.sensor_state[num] = float(st)

            # Schedule HA entity updates
            self.hass.bus.async_fire("teletask_state_updated", {
                "func": func,
                "num": num,
                "state": st
            })

    # ----------------------------------------------------------------------------------------------
    # Lifecycle
    # ----------------------------------------------------------------------------------------------

    def start(self) -> None:
        """Start RX-thread driver and mark hub as running."""
        self.running = True
        self.client.connect()
        _LOGGER.info("TeleTask hub started")

    def stop(self) -> None:
        """Stop the driver and mark hub as not running."""
        self.running = False
        self.client.disconnect()
        _LOGGER.info("TeleTask hub stopped")

    # ----------------------------------------------------------------------------------------------
    # API's called by HA entities
    # ----------------------------------------------------------------------------------------------

    def get_relay_state(self, num: int) -> bool:
        """Get the current state of a relay."""
        return self.relay_state.get(num, False)

    def set_relay_state(self, num: int, value: bool) -> None:
        """Set a relay state."""
        self.client.set_relay(num, "ON" if value else "OFF")

    def get_dimmer_value(self, num: int) -> int:
        """Get the current value of a dimmer (0-255)."""
        return self.dimmer_state.get(num, 0)

    def set_dimmer_value(self, num: int, val: int) -> None:
        """Set a dimmer value (0-255)."""
        self.client.set_dimmer(num, val)

    def get_flag(self, num: int) -> bool:
        """Get the current state of a flag."""
        return self.flag_state.get(num, False)

    def set_flag(self, num: int, value: bool) -> None:
        """Set a flag state."""
        self.client.set_flag(num, "ON" if value else "OFF")

    def get_input_state(self, num: int) -> bool:
        """Get the current state of an input (read-only binary sensor)."""
        return self.input_state.get(num, False)

    def get_sensor_value(self, num: int) -> Optional[float]:
        """Get the current value of an analog sensor."""
        return self.sensor_state.get(num)

    def get_matter_enabled_devices(self) -> Dict[str, set]:
        """
        Get all device numbers where matter=true, grouped by type.

        Returns:
            Dict with keys 'relays', 'dimmers', 'flags', 'inputs', 'sensors'
            and values as sets of device numbers.
        """
        result = {
            "relays": set(),
            "dimmers": set(),
            "flags": set(),
            "inputs": set(),
            "sensors": set(),
        }

        if not self.device_config:
            return result

        # Collect relays with matter=true
        for dev in self.device_config.get_all_relays():
            if dev.matter:
                result["relays"].add(dev.num)

        # Collect dimmers with matter=true
        for dev in self.device_config.get_all_dimmers():
            if dev.matter:
                result["dimmers"].add(dev.num)

        # Collect flags with matter=true
        for dev in self.device_config.get_all_flags():
            if dev.matter:
                result["flags"].add(dev.num)

        # Collect inputs with matter=true
        for dev in self.device_config.get_all_inputs():
            if dev.matter:
                result["inputs"].add(dev.num)

        # Collect sensors with matter=true
        for dev in self.device_config.get_all_sensors():
            if dev.matter:
                result["sensors"].add(dev.num)

        return result
