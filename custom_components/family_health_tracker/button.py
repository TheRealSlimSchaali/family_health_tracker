"""Button platform for Family Health Tracker."""
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
    MEDICATION_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Family Health Tracker buttons."""
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

        record_button = RecordMeasurementButton(hass, member, device_info, config_entry.entry_id)
        entities.append(record_button)

    async_add_entities(entities, True)

class RecordMeasurementButton(ButtonEntity):
    """Button to record measurements."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the button."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._attr_device_info = device_info
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_record_button"
        self._attr_name = "Record Measurement"
        self._attr_icon = "mdi:content-save-plus"  # Add icon

    async def async_press(self) -> None:
        """Handle the button press."""
        # Get all entities to help debug
        all_entities = self._hass.states.async_all()
        entity_ids = [entity.entity_id for entity in all_entities]
        _LOGGER.debug("All available entities: %s", entity_ids)

        # Use the new entity ID format
        temp_input_entity_id = f"number.temperature_{self._name.lower()}"
        med_input_entity_id = f"select.medication_{self._name.lower()}"

        _LOGGER.debug("Looking for temperature entity: %s", temp_input_entity_id)
        _LOGGER.debug("Looking for medication entity: %s", med_input_entity_id)

        temp_state = self._hass.states.get(temp_input_entity_id)
        med_state = self._hass.states.get(med_input_entity_id)

        if temp_state is None or med_state is None:
            _LOGGER.warning(
                "Missing input states for %s. Temperature: %s, Medication: %s",
                self._name,
                temp_state,
                med_state
            )
            return

        try:
            service_data = {
                CONF_NAME: self._name,
                ATTR_TEMPERATURE: float(temp_state.state),
                ATTR_MEDICATION: med_state.state,
            }

            _LOGGER.debug("Calling service with data: %s", service_data)

            await self._hass.services.async_call(
                DOMAIN,
                "add_measurement",
                service_data,
            )
            _LOGGER.debug("Successfully recorded measurement: %s", service_data)

        except Exception as e:
            _LOGGER.error("Failed to call service: %s", e) 