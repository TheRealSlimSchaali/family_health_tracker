"""Config flow for Family Health Tracker integration."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME

from .const import DOMAIN, CONF_MEMBERS, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

class FamilyHealthTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Family Health Tracker."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle the initial step."""
        _LOGGER.debug("Starting config flow user step with input: %s", user_input)

        errors = {}

        if user_input is not None:
            # Validate members input
            members = [m.strip() for m in user_input[CONF_MEMBERS].split(",")]
            if not members:
                errors[CONF_MEMBERS] = "no_members"
            else:
                _LOGGER.debug("Creating entry with data: %s", user_input)
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_MEMBERS): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow changes."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        _LOGGER.debug("Initializing options flow for entry: %s", config_entry.entry_id)

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            _LOGGER.debug("Creating options entry with data: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MEMBERS,
                        default=self.config_entry.data.get(CONF_MEMBERS, ""),
                    ): str,
                }
            ),
        )