"""The Family Health Tracker integration."""
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from .const import DOMAIN, CONF_MEMBERS

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Family Health Tracker component."""
    _LOGGER.debug("Setting up Family Health Tracker integration")

    hass.data.setdefault(DOMAIN, {})

    # Load config entry if it exists
    if DOMAIN in config:
        _LOGGER.debug("Configuration found in configuration.yaml: %s", config[DOMAIN])
        hass.async_create_task(
            hass._config_entries.flow.async_init(
                DOMAIN, context={"source": "import"}, data=config[DOMAIN]
            )
        )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Family Health Tracker from a config entry."""
    _LOGGER.debug("Setting up config entry %s", entry.title)

    try:
        hass.data[DOMAIN][entry.entry_id] = {}

        # Set up all platforms for this device/entry
        _LOGGER.debug("Setting up platforms: %s", PLATFORMS)
        for platform in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )
            _LOGGER.debug("Platform %s setup completed", platform)

        return True

    except Exception as ex:
        _LOGGER.error("Error setting up entry: %s", str(ex))
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading config entry %s", entry.title)

    try:
        unload_ok = all(
            await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, platform)
                    for platform in PLATFORMS
                ]
            )
        )

        if unload_ok:
            _LOGGER.debug("Successfully unloaded entry")
            hass.data[DOMAIN].pop(entry.entry_id)
        else:
            _LOGGER.error("Failed to unload entry")

        return unload_ok

    except Exception as ex:
        _LOGGER.error("Error unloading entry: %s", str(ex))
        return False