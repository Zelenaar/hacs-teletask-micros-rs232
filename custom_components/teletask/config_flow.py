
#################################################################################################
# File:    config_flow.py
# Version: 1.0
#################################################################################################

import voluptuous as vol
from homeassistant import config_entries

from . import DOMAIN

class TeletaskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """TeleTask MICROS config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="TeleTask MICROS", data=user_input)

        schema = vol.Schema({
            vol.Required("serial_port", default="COM6"): str
        })

        return self.async_show_form(step_id="user", data_schema=schema)
