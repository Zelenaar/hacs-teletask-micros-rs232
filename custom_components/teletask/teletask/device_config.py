
#################################################################################################
# File:    device_config.py
# Version: 1.4
#
# Description:
#   Loader for TeleTask device configuration.
#   Provides device definitions (num, name, room, icon, type, ha, matter) for GUI and HA.
#   Supports: relays, dimmers, flags, moods, inputs (binary), sensors (analog).
#   - ha: whether to expose device to Home Assistant
#   - matter: whether to expose via Matter (only if ha=true)
#################################################################################################

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DeviceInfo:
    """Information about a single TeleTask device."""
    num: int
    name: str
    room: str = ""
    icon: str = ""
    type: str = ""  # For moods: LOCAL or GENERAL; for relays: light or switch
    ha: bool = True  # Expose to Home Assistant
    matter: bool = False  # Expose via Matter (only if ha=True)

    @property
    def display_name(self) -> str:
        """Return formatted display name with room prefix."""
        if self.room:
            return f"{self.room} - {self.name}"
        return self.name


@dataclass
class SensorInfo:
    """Information about a TeleTask analog sensor (temperature, humidity, etc.)."""
    num: int
    name: str
    room: str = ""
    icon: str = ""
    type: str = ""  # temperature, humidity, light, etc.
    unit: str = ""  # °C, %, lux, etc.
    ha: bool = True  # Expose to Home Assistant
    matter: bool = False  # Expose via Matter (only if ha=True)

    @property
    def display_name(self) -> str:
        """Return formatted display name with room prefix."""
        if self.room:
            return f"{self.room} - {self.name}"
        return self.name


@dataclass
class DeviceConfig:
    """Container for all device configurations."""
    relays: Dict[int, DeviceInfo] = field(default_factory=dict)
    dimmers: Dict[int, DeviceInfo] = field(default_factory=dict)
    flags: Dict[int, DeviceInfo] = field(default_factory=dict)
    local_moods: Dict[int, DeviceInfo] = field(default_factory=dict)
    general_moods: Dict[int, DeviceInfo] = field(default_factory=dict)
    timed_moods: Dict[int, DeviceInfo] = field(default_factory=dict)
    inputs: Dict[int, DeviceInfo] = field(default_factory=dict)
    sensors: Dict[int, SensorInfo] = field(default_factory=dict)

    def get_relay(self, num: int) -> Optional[DeviceInfo]:
        """Get relay info by number."""
        return self.relays.get(num)

    def get_dimmer(self, num: int) -> Optional[DeviceInfo]:
        """Get dimmer info by number."""
        return self.dimmers.get(num)

    def get_flag(self, num: int) -> Optional[DeviceInfo]:
        """Get flag info by number."""
        return self.flags.get(num)

    def get_mood(self, num: int, mood_type: str = "LOCAL") -> Optional[DeviceInfo]:
        """Get mood info by number and type."""
        mood_upper = mood_type.upper()
        if mood_upper == "GENERAL":
            return self.general_moods.get(num)
        elif mood_upper == "TIMED":
            return self.timed_moods.get(num)
        return self.local_moods.get(num)

    def get_input(self, num: int) -> Optional[DeviceInfo]:
        """Get input info by number."""
        return self.inputs.get(num)

    def get_sensor(self, num: int) -> Optional[SensorInfo]:
        """Get sensor info by number."""
        return self.sensors.get(num)

    def get_all_relays(self) -> List[DeviceInfo]:
        """Get all configured relays sorted by number."""
        return sorted(self.relays.values(), key=lambda d: d.num)

    def get_all_dimmers(self) -> List[DeviceInfo]:
        """Get all configured dimmers sorted by number."""
        return sorted(self.dimmers.values(), key=lambda d: d.num)

    def get_all_flags(self) -> List[DeviceInfo]:
        """Get all configured flags sorted by number."""
        return sorted(self.flags.values(), key=lambda d: d.num)

    def get_all_moods(self) -> List[DeviceInfo]:
        """Get all configured moods (local + general + timed) sorted by type and number."""
        local = sorted(self.local_moods.values(), key=lambda d: d.num)
        general = sorted(self.general_moods.values(), key=lambda d: d.num)
        timed = sorted(self.timed_moods.values(), key=lambda d: d.num)
        return local + general + timed

    def get_all_inputs(self) -> List[DeviceInfo]:
        """Get all configured inputs sorted by number."""
        return sorted(self.inputs.values(), key=lambda d: d.num)

    def get_all_sensors(self) -> List[SensorInfo]:
        """Get all configured sensors sorted by number."""
        return sorted(self.sensors.values(), key=lambda d: d.num)


def load_device_config(config_path: str = "config/devices.json") -> DeviceConfig:
    """
    Load device configuration from JSON file.

    Args:
        config_path: Path to the devices.json file.

    Returns:
        DeviceConfig with all device definitions.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config file is invalid.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Device config not found: {config_path}. "
            f"Create it with relay, dimmer, flag, and mood definitions."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in device config: {e}")

    config = DeviceConfig()

    # Parse relays
    for item in data.get("relays", []):
        num = item.get("num")
        if num is not None:
            config.relays[num] = DeviceInfo(
                num=num,
                name=item.get("name", f"Relay {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type=item.get("type", ""),
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    # Parse dimmers
    for item in data.get("dimmers", []):
        num = item.get("num")
        if num is not None:
            config.dimmers[num] = DeviceInfo(
                num=num,
                name=item.get("name", f"Dimmer {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type=item.get("type", ""),
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    # Parse flags
    for item in data.get("flags", []):
        num = item.get("num")
        if num is not None:
            config.flags[num] = DeviceInfo(
                num=num,
                name=item.get("name", f"Flag {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type=item.get("type", ""),
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    # Parse moods - support both old "moods" format and new separate keys
    # Old format: "moods" array with "type" field
    for item in data.get("moods", []):
        num = item.get("num")
        mood_type = item.get("type", "LOCAL").upper()
        if num is not None:
            info = DeviceInfo(
                num=num,
                name=item.get("name", f"Mood {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type=mood_type,
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )
            if mood_type == "GENERAL":
                config.general_moods[num] = info
            elif mood_type == "TIMED":
                config.timed_moods[num] = info
            else:
                config.local_moods[num] = info

    # New format: separate "local_moods", "general_moods", "timed_moods" arrays
    for item in data.get("local_moods", []):
        num = item.get("num")
        if num is not None:
            config.local_moods[num] = DeviceInfo(
                num=num,
                name=item.get("name", f"Local Mood {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type="LOCAL",
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    for item in data.get("general_moods", []):
        num = item.get("num")
        if num is not None:
            config.general_moods[num] = DeviceInfo(
                num=num,
                name=item.get("name", f"General Mood {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type="GENERAL",
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    for item in data.get("timed_moods", []):
        num = item.get("num")
        if num is not None:
            config.timed_moods[num] = DeviceInfo(
                num=num,
                name=item.get("name", f"Timed Mood {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type="TIMED",
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    # Parse inputs (digital inputs / binary sensors)
    for item in data.get("inputs", []):
        num = item.get("num")
        if num is not None:
            config.inputs[num] = DeviceInfo(
                num=num,
                name=item.get("name", f"Input {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type=item.get("type", ""),
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    # Parse sensors (analog sensors)
    for item in data.get("sensors", []):
        num = item.get("num")
        if num is not None:
            config.sensors[num] = SensorInfo(
                num=num,
                name=item.get("name", f"Sensor {num}"),
                room=item.get("room", ""),
                icon=item.get("icon", ""),
                type=item.get("type", ""),
                unit=item.get("unit", ""),
                ha=item.get("ha", True),
                matter=item.get("matter", False)
            )

    return config


def load_device_config_safe(config_path: str = "config/devices.json") -> Optional[DeviceConfig]:
    """
    Load device configuration, returning None if file doesn't exist.

    This is useful for optional configuration - if no devices.json exists,
    the application can fall back to default behavior.
    """
    try:
        return load_device_config(config_path)
    except FileNotFoundError:
        return None
    except ValueError as e:
        print(f"[WARN] Device config error: {e}")
        return None
