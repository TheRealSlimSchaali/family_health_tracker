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

        temp_entity_id = f"sensor.health_tracker_{name.lower()}_temperature"
        med_entity_id = f"sensor.health_tracker_{name.lower()}_medication"

        _LOGGER.debug("Looking for sensors: %s and %s", temp_entity_id, med_entity_id)

        for entry_id in hass.data[DOMAIN]:
            if temp_entity_id in hass.data[DOMAIN][entry_id]:
                temp_sensor = hass.data[DOMAIN][entry_id][temp_entity_id]
                med_sensor = hass.data[DOMAIN][entry_id][med_entity_id]

                temp_sensor.update_temperature(temperature)
                med_sensor.update_medication(medication)

                _LOGGER.debug(
                    "Updated measurements for %s: temp=%f, med=%s",
                    name, temperature, medication
                )
                return

        _LOGGER.error("No sensors found for %s", name)

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

    # Set up all platforms for this device/entry
    for platform in PLATFORMS:
        try:
            _LOGGER.debug("Setting up platform: %s", platform)
            await hass.config_entries.async_forward_entry_setup(entry, platform)
            _LOGGER.debug("Successfully set up platform: %s", platform)
        except Exception as ex:
            _LOGGER.error("Error setting up platform %s: %s", platform, str(ex))
            return False

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = True

    for platform in PLATFORMS:
        try:
            unloaded = await hass.config_entries.async_forward_entry_unload(entry, platform)
            if not unloaded:
                _LOGGER.error("Failed to unload platform: %s", platform)
                unload_ok = False
        except Exception as ex:
            _LOGGER.error("Error unloading platform %s: %s", platform, str(ex))
            unload_ok = False

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok