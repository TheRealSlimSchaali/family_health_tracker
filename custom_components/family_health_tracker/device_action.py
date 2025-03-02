"""Provides device actions for Family Health Tracker."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import device_registry as dr
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
    VERSION,
    get_medication_values,
)

ACTION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): str,
        vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
        vol.Required(ATTR_MEDICATION): vol.In(get_medication_values()),
    }
)

async def async_setup_device_registry_entry_action(
    hass: HomeAssistant,
    config_entry_id: str,
    device_id: str,
    action_type: str,
) -> dict:
    """Set up device registry entry action."""
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)

    if not device:
        return None

    # Check if this is our device
    if not any(x[0] == DOMAIN for x in device.identifiers):
        return None

    return {
        "title": "Record Measurement",
        "action_type": "record_measurement",
        "fields": [
            {
                "name": ATTR_TEMPERATURE,
                "required": True,
                "type": "float",
                "description": "Temperature (34-43°C)",
            },
            {
                "name": ATTR_MEDICATION,
                "required": True,
                "type": "select",
                "options": get_medication_values(),
                "description": "Select medication",
            },
        ],
    } 