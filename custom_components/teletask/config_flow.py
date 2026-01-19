
#################################################################################################
# File:    config_flow.py
# Version: 1.1 - Cross-platform default, duplicate prevention, type hints
#################################################################################################

import platform
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN

# Platform-specific default serial ports
DEFAULT_SERIAL_PORTS = {
    "Windows": "COM6",
    "Linux": "/dev/ttyUSB0",
    "Darwin": "/dev/tty.usbserial",  # macOS
}


class TeletaskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """TeleTask MICROS config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial user configuration step."""
        # Prevent duplicate configurations
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="TeleTask MICROS", data=user_input)

        # Get platform-specific default serial port
        system = platform.system()
        default_port = DEFAULT_SERIAL_PORTS.get(system, "/dev/ttyUSB0")

        schema = vol.Schema({
            vol.Required("serial_port", default=default_port): str
        })

        return self.async_show_form(step_id="user", data_schema=schema)
