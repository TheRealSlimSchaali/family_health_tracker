"""The Family Health Tracker integration."""
import logging
from typing import Any
from datetime import datetime

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
    VERSION,
    get_medication_values,
    CONF_MEDICATIONS,
    DEFAULT_MEDICATIONS,
    get_combined_medications
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_MEMBERS): cv.string,
        vol.Optional(CONF_MEDICATIONS, default=DEFAULT_MEDICATIONS): {
            cv.string: {
                vol.Required("name"): cv.string,
                vol.Required("label"): cv.string,
                vol.Optional("dosage"): cv.string,
                vol.Optional("interval_hours"): cv.positive_int,
                vol.Optional("category"): cv.string,
            }
        }
    })
}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor", "number", "select", "button"]

MEASUREMENT_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
    vol.Required(ATTR_MEDICATION): vol.In(get_medication_values())
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
    # Initialize storage for this entry
    hass.data[DOMAIN][entry.entry_id] = {}
    
    # Store medications in hass.data
    hass.data[DOMAIN][CONF_MEDICATIONS] = entry.options.get(CONF_MEDICATIONS, {})

    # Register services
    async def add_measurement(call: ServiceCall) -> None:
        """Add a new measurement."""
        name = call.data[CONF_NAME]
        temperature = call.data[ATTR_TEMPERATURE]
        medication = call.data[ATTR_MEDICATION]

        # Get the correct entities
        name_lower = name.lower()
        temp_entity_id = f"sensor.temperature_{name_lower}"
        med_entity_id = f"sensor.medication_{name_lower}"

        temp_sensor = hass.data[DOMAIN][entry.entry_id].get(temp_entity_id)
        med_sensor = hass.data[DOMAIN][entry.entry_id].get(med_entity_id)

        if temp_sensor is None or med_sensor is None:
            raise HomeAssistantError(f"Could not find sensors for {name}")

        await temp_sensor.update_temperature(temperature)
        await med_sensor.update_medication(medication)

    hass.services.async_register(
        DOMAIN,
        "add_measurement",
        add_measurement,
        schema=MEASUREMENT_SERVICE_SCHEMA,
    )

    async def get_medications(call: ServiceCall) -> None:
        """Get all configured medications."""
        user_medications = hass.data[DOMAIN].get(CONF_MEDICATIONS, {})
        all_medications = get_combined_medications(user_medications)
        
        # Create a persistent entity
        entity_id = f"{DOMAIN}.medication_library"
        
        # Format the response
        formatted_meds = {}
        for med_id, med_info in all_medications.items():
            formatted_meds[med_id] = {
                "name": med_info["name"],
                "label": med_info["label"],
                "dosage": med_info.get("dosage"),
                "interval_hours": med_info.get("interval_hours"),
                "category": med_info.get("category", "other")
            }
        
        # Set state with attributes
        hass.states.async_set(
            entity_id,
            len(formatted_meds),  # Number of medications as state
            {
                "medications": formatted_meds,
                "last_updated": datetime.now().isoformat()
            }
        )

    # Register with schema
    GET_MEDICATIONS_SCHEMA = vol.Schema({})

    hass.services.async_register(
        DOMAIN,
        "get_medications",
        get_medications,
        schema=GET_MEDICATIONS_SCHEMA,
    )

    # Create a hub device first
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="Family Health Tracker",
        manufacturer="Family Health Tracker",
        model="Hub",
        sw_version=VERSION,
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
            sw_version=VERSION,
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