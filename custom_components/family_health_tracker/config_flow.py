"""Config flow for Family Health Tracker."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    CONF_MEDICATIONS,
    DEFAULT_MEDICATIONS,
    ATTR_DOSAGE,
    ATTR_INTERVAL,
    ATTR_CATEGORY,
)

_LOGGER = logging.getLogger(__name__)

class FamilyHealthTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Family Health Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            if not user_input[CONF_MEMBERS]:
                errors["base"] = "no_members"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="Health Tracker"): str,
                vol.Required(CONF_MEMBERS): str,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Family Health Tracker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            if user_input["step"] == "members":
                return await self.async_step_members()
            else:
                return await self.async_step_medication()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("step", default="members"): vol.In({
                    "members": "Manage Family Members",
                    "medication": "Add Medication"
                })
            })
        )

    async def async_step_members(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle family members step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="members",
            data_schema=vol.Schema({
                vol.Required(CONF_MEMBERS, default=self.config_entry.data[CONF_MEMBERS]): str,
            }),
        )

    async def async_step_medication(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle medication configuration."""
        if user_input is not None:
            medications = self.config_entry.options.get(CONF_MEDICATIONS, {})
            med_id = user_input.pop("id").lower().replace(" ", "_")
            medications[med_id] = {
                "name": user_input["name"],
                "label": user_input["label"],
                "dosage": user_input.get("dosage"),
                "interval_hours": user_input.get("interval_hours"),
                "category": user_input.get("category", "other")
            }
            return self.async_create_entry(
                title="",
                data={CONF_MEDICATIONS: medications}
            )

        return self.async_show_form(
            step_id="medication",
            data_schema=vol.Schema({
                vol.Required("id"): str,
                vol.Required("name"): str,
                vol.Required("label"): str,
                vol.Optional(ATTR_DOSAGE): str,
                vol.Optional(ATTR_INTERVAL): vol.Coerce(int),
                vol.Optional(ATTR_CATEGORY): str,
            }),
            description_placeholders={
                "example": "Example: ibuprofen_kids, Ibuprofen Kids, 100mg/5ml, 6, nsaid"
            }
        )