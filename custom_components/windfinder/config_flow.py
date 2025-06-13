"""Config flow for Windfinder integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_LOCATION,
    CONF_INITIAL_REFRESH,
    DEFAULT_INITIAL_REFRESH,
)

class WindfinderConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Windfinder."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_LOCATION], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_LOCATION): str}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WindfinderOptionsFlowHandler(config_entry)

class WindfinderOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LOCATION, default=self.config_entry.data.get(CONF_LOCATION)
                    ): str,
                    vol.Required(
                        CONF_INITIAL_REFRESH,
                        default=self.config_entry.options.get(
                            CONF_INITIAL_REFRESH, DEFAULT_INITIAL_REFRESH
                        ),
                    ): int,
                }
            ),
        )
