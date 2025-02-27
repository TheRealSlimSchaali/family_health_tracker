"""The Family Health Tracker integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
    MEDICATION_OPTIONS
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_MEMBERS): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]

MEASUREMENT_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
    vol.Required(ATTR_MEDICATION): vol.In(MEDICATION_OPTIONS)
})

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Family Health Tracker component."""
    _LOGGER.debug("Setting up Family Health Tracker integration")

    if DOMAIN not in config:
        return True

    hass.data.setdefault(DOMAIN, {})

    async def handle_add_measurement(call: ServiceCall) -> None:
        """Handle the service call."""
        name = call.data.get(CONF_NAME)
        temperature = call.data.get(ATTR_TEMPERATURE)
        medication = call.data.get(ATTR_MEDICATION)

        # Convert name to lowercase for consistent matching
        name_lower = name.lower()
        temp_entity_id = f"sensor.health_tracker_{name_lower}_temperature"
        med_entity_id = f"sensor.health_tracker_{name_lower}_medication"

        _LOGGER.debug("Looking for sensors: %s and %s", temp_entity_id, med_entity_id)

        # Search through all config entries
        found = False
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if temp_entity_id in entry_data and med_entity_id in entry_data:
                temp_sensor = entry_data[temp_entity_id]
                med_sensor = entry_data[med_entity_id]

                await temp_sensor.update_temperature(temperature)
                await med_sensor.update_medication(medication)

                _LOGGER.debug(
                    "Updated measurements for %s: temp=%f, med=%s",
                    name, temperature, medication
                )
                found = True
                break

        if not found:
            _LOGGER.error(
                "No sensors found for %s. Available sensors: %s",
                name,
                str(hass.data[DOMAIN])
            )

    hass.services.async_register(
        DOMAIN,
        "add_measurement",
        handle_add_measurement,
        schema=MEASUREMENT_SERVICE_SCHEMA
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Family Health Tracker from a config entry."""
    _LOGGER.debug("Setting up config entry: %s", entry.data)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    _LOGGER.debug("Starting platform setup for: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry %s", entry.entry_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Successfully unloaded entry %s", entry.entry_id)

    return unload_ok