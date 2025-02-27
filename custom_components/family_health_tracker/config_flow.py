"""Config flow for Family Health Tracker integration."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    DEFAULT_NAME,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
    MEDICATION_OPTIONS,
)

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
        super().__init__(config_entry)
        _LOGGER.debug("Initializing options flow for entry: %s", config_entry.entry_id)

    async def async_step_init(self, user_input=None):
        """Handle options flow initial step."""
        return await self.async_step_menu()

    async def async_step_menu(self, user_input=None):
        """Show the menu for options flow."""
        if user_input is not None:
            if user_input["menu_option"] == "update_members":
                return await self.async_step_update_members()
            else:
                return await self.async_step_record_measurement()

        return self.async_show_form(
            step_id="menu",
            data_schema=vol.Schema({
                vol.Required("menu_option", default="record_measurement"): vol.In({
                    "record_measurement": "Record New Measurement",
                    "update_members": "Update Family Members",
                })
            })
        )

    async def async_step_update_members(self, user_input=None):
        """Handle the update members step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="update_members",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_MEMBERS,
                    default=self._config_entry.data.get(CONF_MEMBERS, ""),
                ): str,
            })
        )

    async def async_step_record_measurement(self, user_input=None):
        """Handle the record measurement step."""
        errors = {}

        if user_input is not None:
            temperature = user_input[ATTR_TEMPERATURE]
            # Validate temperature is in a reasonable range (35-42°C)
            if temperature < 35 or temperature > 42:
                errors[ATTR_TEMPERATURE] = "temperature_invalid"
            else:
                # Process the measurement
                selected_member = user_input["selected_member"]
                medication = user_input[ATTR_MEDICATION]

                # Call our service to record the measurement
                await self.hass.services.async_call(
                    DOMAIN,
                    "add_measurement",
                    {
                        CONF_NAME: selected_member,
                        ATTR_TEMPERATURE: temperature,
                        ATTR_MEDICATION: medication,
                    },
                )

                # Show success and return to menu
                return self.async_show_progress_done(next_step_id="menu")

        members = [m.strip() for m in self._config_entry.data[CONF_MEMBERS].split(",")]
        measurement_schema = vol.Schema({
            vol.Required("selected_member"): vol.In(members),
            vol.Required(ATTR_TEMPERATURE, description="Enter temperature between 35-42°C"): vol.Coerce(float),
            vol.Required(ATTR_MEDICATION): vol.In({
                "none": "No medication given",
                "paracetamol": "Paracetamol administered",
                "ibuprofen": "Ibuprofen administered",
            }),
        })

        return self.async_show_form(
            step_id="record_measurement",
            data_schema=measurement_schema,
            errors=errors,
        )