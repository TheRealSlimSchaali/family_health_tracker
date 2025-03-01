"""Number platform for Family Health Tracker."""
import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME, UnitOfTemperature

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Family Health Tracker number inputs."""
    members = [member.strip() for member in config_entry.data[CONF_MEMBERS].split(",")]

    entities = []
    for member in members:
        member_lower = member.lower()
        device_id = f"{config_entry.entry_id}_{member_lower}"
        
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=member,
            manufacturer="Family Health Tracker",
            model="Health Monitor",
            sw_version="1.0",
            via_device=(DOMAIN, config_entry.entry_id),
        )

        temp_input = TemperatureInput(hass, member, device_info, config_entry.entry_id)
        entities.append(temp_input)

    async_add_entities(entities, True)

class TemperatureInput(NumberEntity):
    """Temperature input for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the input."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._attr_device_info = device_info
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_temperature_input"
        self._attr_name = "Temperature Input"
        self._attr_native_min_value = 34.0
        self._attr_native_max_value = 43.0
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_mode = "box"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._hass.services.async_call(
            DOMAIN,
            "add_measurement",
            {
                CONF_NAME: self._name,
                ATTR_TEMPERATURE: value,
                ATTR_MEDICATION: "none",  # Default value
            },
        ) 