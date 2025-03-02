"""Select platform for Family Health Tracker."""
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME, UnitOfTemperature

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    MEDICATION_OPTIONS,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Family Health Tracker select inputs."""
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

        med_input = MedicationInput(hass, member, device_info, config_entry.entry_id)
        entities.append(med_input)
        
        # Debug log the entity ID being created
        _LOGGER.debug(
            "Creating medication input entity with ID: select.%s_%s_medication_input",
            config_entry.entry_id,
            member_lower
        )

    async_add_entities(entities, True)

class MedicationInput(SelectEntity):
    """Medication input for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the input."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._attr_device_info = device_info
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_medication_input"
        self.entity_id = f"select.medication_{name.lower()}"
        self._attr_name = f"{name} Medication Input"
        self._attr_icon = "mdi:pill"
        # Store the full options for label lookup
        self._options_map = {opt["value"]: opt["label"] for opt in MEDICATION_OPTIONS}
        # Set options to just the values
        self._attr_options = [opt["value"] for opt in MEDICATION_OPTIONS]
        self._attr_current_option = self._attr_options[0]
        self._attr_translation_key = "medication_input"  # Add this for sorting

    @property
    def state(self) -> str:
        """Return the state - use the label instead of the value."""
        return self._options_map.get(self._attr_current_option, self._attr_current_option)

    async def async_select_option(self, option: str) -> None:
        """Update the current value."""
        _LOGGER.debug("Medication selected: %s for %s", option, self._name)
        
        # Update our state first
        self._attr_current_option = option
        self.async_write_ha_state()