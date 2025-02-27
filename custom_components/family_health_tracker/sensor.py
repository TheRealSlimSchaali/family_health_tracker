"""Sensor platform for Family Health Tracker."""
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import TEMP_CELSIUS, CONF_NAME

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
    """Set up the Family Health Tracker sensor."""
    _LOGGER.debug("Setting up sensors for config entry: %s", config_entry.data)

    name = config_entry.data[CONF_NAME]
    members_str = config_entry.data[CONF_MEMBERS]
    members = [member.strip() for member in members_str.split(",")]

    _LOGGER.debug("Creating sensors for members: %s", members)

    sensors = []
    for member in members:
        _LOGGER.debug("Creating sensors for member: %s", member)

        temp_sensor = TemperatureSensor(hass, member, config_entry.entry_id)
        med_sensor = MedicationSensor(hass, member, config_entry.entry_id)
        sensors.extend([temp_sensor, med_sensor])

        # Store sensor references for service calls
        entity_id_temp = f"sensor.health_tracker_{member.lower()}_temperature"
        entity_id_med = f"sensor.health_tracker_{member.lower()}_medication"

        _LOGGER.debug("Registering sensors with IDs: %s, %s", entity_id_temp, entity_id_med)

        hass.data[DOMAIN][config_entry.entry_id][entity_id_temp] = temp_sensor
        hass.data[DOMAIN][config_entry.entry_id][entity_id_med] = med_sensor

    _LOGGER.debug("Adding %d sensors to Home Assistant", len(sensors))
    async_add_entities(sensors, True)
    _LOGGER.debug("Sensor setup complete")

class TemperatureSensor(SensorEntity):
    """Temperature sensor for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, entry_id: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = None
        self._last_updated = None

        # Set required attributes for proper entity setup
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = TEMP_CELSIUS
        self._attr_unique_id = f"{DOMAIN}_{name.lower()}_temperature"
        self._attr_has_entity_name = True
        self._attr_name = f"{name} Temperature"

        self._attributes = {
            "last_measurement": None,
            "last_updated": None
        }
        _LOGGER.debug("Initialized temperature sensor: %s", self._attr_unique_id)

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    def update_temperature(self, temperature: float) -> None:
        """Update temperature measurement."""
        self._state = temperature
        self._last_updated = datetime.now().isoformat()
        self._attributes["last_measurement"] = temperature
        self._attributes["last_updated"] = self._last_updated
        self.schedule_update_ha_state()
        _LOGGER.debug(
            "Updated temperature for %s: %f %s at %s",
            self._name,
            temperature,
            self.native_unit_of_measurement,
            self._last_updated
        )

class MedicationSensor(SensorEntity):
    """Medication sensor for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, entry_id: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = "none"
        self._last_updated = None

        # Set required attributes for proper entity setup
        self._attr_unique_id = f"{DOMAIN}_{name.lower()}_medication"
        self._attr_has_entity_name = True
        self._attr_name = f"{name} Medication"

        self._attributes = {
            "last_medication": None,
            "last_updated": None
        }
        _LOGGER.debug("Initialized medication sensor: %s", self._attr_unique_id)

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    def update_medication(self, medication: str) -> None:
        """Update medication status."""
        self._state = medication
        self._last_updated = datetime.now().isoformat()
        self._attributes["last_medication"] = medication
        self._attributes["last_updated"] = self._last_updated
        self.schedule_update_ha_state()
        _LOGGER.debug(
            "Updated medication for %s: %s at %s",
            self._name,
            medication,
            self._last_updated
        )