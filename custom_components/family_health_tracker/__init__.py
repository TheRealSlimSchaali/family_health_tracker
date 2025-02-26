"""The Family Health Tracker integration."""
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional

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

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]

MEASUREMENT_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
    vol.Required(ATTR_MEDICATION): vol.In(MEDICATION_OPTIONS)
})

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Family Health Tracker component."""
    _LOGGER.debug("BEGIN async_setup for Family Health Tracker integration")
    _LOGGER.debug("Config contents: %s", config)

    try:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.debug("Initialized hass.data[%s]", DOMAIN)

        async def handle_add_measurement(call: ServiceCall) -> None:
            """Handle the service call."""
            name = call.data.get(CONF_NAME)
            temperature = call.data.get(ATTR_TEMPERATURE)
            medication = call.data.get(ATTR_MEDICATION)

            _LOGGER.debug(
                "Service called - name: %s, temp: %f, medication: %s",
                name, temperature, medication
            )

            # Find the correct sensor entity
            entity_id = f"sensor.health_tracker_{name.lower()}"
            sensor = hass.states.get(entity_id)

            if sensor is None:
                _LOGGER.error("No sensor found for %s", name)
                return

            # Get the sensor object and add the measurement
            for entry_id in hass.data[DOMAIN]:
                if entity_id in hass.data[DOMAIN][entry_id]:
                    sensor_obj = hass.data[DOMAIN][entry_id][entity_id]
                    await hass.async_add_executor_job(
                        sensor_obj.add_measurement, temperature, medication
                    )
                    _LOGGER.debug("Measurement added successfully")
                    return

            _LOGGER.error("Could not find sensor object for %s", name)

        # Register our services
        hass.services.async_register(
            DOMAIN,
            "add_measurement",
            handle_add_measurement,
            schema=MEASUREMENT_SERVICE_SCHEMA
        )
        _LOGGER.debug("Registered add_measurement service")

        # Load config entry if it exists
        if DOMAIN in config:
            _LOGGER.debug("Found configuration in configuration.yaml: %s", config[DOMAIN])
            _LOGGER.debug("Initializing config entry from yaml import")
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": "import"}, data=config[DOMAIN]
                )
            )
            _LOGGER.debug("Config entry initialization task created")
        else:
            _LOGGER.debug("No configuration found in configuration.yaml")

        _LOGGER.debug("END async_setup - Completed successfully")
        return True

    except Exception as ex:
        _LOGGER.error("ERROR in async_setup: %s", str(ex), exc_info=True)
        return False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Family Health Tracker from a config entry."""
    _LOGGER.debug("BEGIN async_setup_entry for entry_id: %s", entry.entry_id)
    _LOGGER.debug("Entry data: %s", entry.data)

    try:
        _LOGGER.debug("Initializing component data storage")
        hass.data[DOMAIN][entry.entry_id] = {}

        # Set up all platforms for this device/entry
        _LOGGER.debug("Starting platform setup for: %s", PLATFORMS)
        for platform in PLATFORMS:
            _LOGGER.debug("Setting up platform: %s", platform)
            try:
                setup_task = hass.config_entries.async_forward_entry_setup(entry, platform)
                await setup_task
                _LOGGER.debug("Successfully set up platform: %s", platform)
            except Exception as platform_ex:
                _LOGGER.error("Failed to set up platform %s: %s", platform, str(platform_ex), exc_info=True)
                raise

        _LOGGER.debug("END async_setup_entry - Completed successfully")
        return True

    except Exception as ex:
        _LOGGER.error("ERROR in async_setup_entry: %s", str(ex), exc_info=True)
        # Clean up any partial setup
        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("BEGIN async_unload_entry for entry_id: %s", entry.entry_id)

    try:
        _LOGGER.debug("Starting platform unload for: %s", PLATFORMS)
        unload_ok = all(
            await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, platform)
                    for platform in PLATFORMS
                ]
            )
        )

        if unload_ok:
            _LOGGER.debug("Successfully unloaded all platforms")
            hass.data[DOMAIN].pop(entry.entry_id)
            _LOGGER.debug("Removed entry data from hass.data")
        else:
            _LOGGER.error("Failed to unload one or more platforms")

        _LOGGER.debug("END async_unload_entry - Success: %s", unload_ok)
        return unload_ok

    except Exception as ex:
        _LOGGER.error("ERROR in async_unload_entry: %s", str(ex), exc_info=True)
        return False