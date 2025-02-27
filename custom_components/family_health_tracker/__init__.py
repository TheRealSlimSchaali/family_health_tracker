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
    if DOMAIN not in config:
        return True

    hass.data.setdefault(DOMAIN, {})

    async def handle_add_measurement(call: ServiceCall) -> None:
        """Handle the service call."""
        name = call.data.get(CONF_NAME)
        temperature = call.data.get(ATTR_TEMPERATURE)
        medication = call.data.get(ATTR_MEDICATION)

        entity_id = f"sensor.health_tracker_{name.lower()}"

        for entry_id in hass.data[DOMAIN]:
            if entity_id in hass.data[DOMAIN][entry_id]:
                sensor = hass.data[DOMAIN][entry_id][entity_id]
                sensor.add_measurement(temperature)
                _LOGGER.debug("Added measurement for %s: temp=%f", name, temperature)
                return

        _LOGGER.error("No sensor found for %s", name)

    hass.services.async_register(
        DOMAIN,
        "add_measurement",
        handle_add_measurement,
        schema=MEASUREMENT_SERVICE_SCHEMA
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Family Health Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok