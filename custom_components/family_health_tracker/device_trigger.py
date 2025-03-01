"""Provides device triggers for Family Health Tracker."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, ATTR_TEMPERATURE, ATTR_MEDICATION, MEDICATION_OPTIONS, MEDICATION_VALUES

TRIGGER_TYPES = {"record_measurement"}

TRIGGER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLATFORM): "device",
        vol.Required(CONF_DOMAIN): DOMAIN,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
        vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
        vol.Required(ATTR_MEDICATION): vol.In(MEDICATION_VALUES),
    }
)

async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device triggers for Family Health Tracker devices."""
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)

    if not device:
        return []

    # Check if this is our device
    if not any(x[0] == DOMAIN for x in device.identifiers):
        return []

    triggers = []

    # Add the record measurement trigger
    triggers.append({
        CONF_PLATFORM: "device",
        CONF_DOMAIN: DOMAIN,
        CONF_DEVICE_ID: device_id,
        CONF_TYPE: "record_measurement",
        "metadata": {
            "secondary": False,
            "description": "Record a new measurement",
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
                    "options": [
                        {"value": "none", "label": "No medication given"},
                        {"value": "paracetamol", "label": "Paracetamol administered"},
                        {"value": "ibuprofen", "label": "Ibuprofen administered"},
                    ],
                    "description": "Select medication",
                },
            ],
        },
    })

    return triggers 