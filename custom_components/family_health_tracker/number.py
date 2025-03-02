"""Number platform for Family Health Tracker."""
import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
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
            sw_version=VERSION,
            via_device=(DOMAIN, config_entry.entry_id),
        )

        temp_input = TemperatureInput(hass, member, device_info, config_entry.entry_id)
        entities.append(temp_input)
        
        # Debug log the entity ID being created
        _LOGGER.debug(
            "Creating temperature input entity with ID: number.%s_%s_temperature_input",
            config_entry.entry_id,
            member_lower
        )

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
        self.entity_id = f"number.temperature_{name.lower()}"
        self._attr_name = f"{name} Temperature Input"
        self._attr_icon = "mdi:thermometer"
        self._attr_native_min_value = 35.0
        self._attr_native_max_value = 42.0
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_mode = NumberMode.BOX
        self._attr_translation_key = "temperature_input"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()
        # Remove the automatic service call from here 