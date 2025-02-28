"""The Family Health Tracker integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_NAME, CONF_DEVICE_ID
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.exceptions import HomeAssistantError

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

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Family Health Tracker from a config entry."""
    _LOGGER.debug("Setting up config entry: %s", entry.data)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    # Create a hub device first
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="Family Health Tracker",
        manufacturer="Family Health Tracker",
        model="Hub",
        sw_version="1.0",
    )

    # Register devices for each family member
    members = [m.strip() for m in entry.data[CONF_MEMBERS].split(",")]
    
    for member in members:
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f"{entry.entry_id}_{member.lower()}")},
            name=f"{member}",
            manufacturer="Family Health Tracker",
            model="Health Monitor",
            sw_version="1.0",
            via_device=(DOMAIN, entry.entry_id),
            entry_type="service",  # This is important for showing the configuration section
        )

    _LOGGER.debug("Starting platform setup for: %s", PLATFORMS)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry %s", entry.entry_id)

    # Remove the service when the last config entry is unloaded
    if len(hass.data[DOMAIN]) == 1:
        hass.services.async_remove(DOMAIN, "add_measurement")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Clean up devices
        device_registry = dr.async_get(hass)
        devices = dr.async_entries_for_config_entry(
            device_registry, entry.entry_id
        )
        for device in devices:
            device_registry.async_remove_device(device.id)

        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Successfully unloaded entry %s", entry.entry_id)

    return unload_ok