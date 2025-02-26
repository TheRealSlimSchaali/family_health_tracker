"""Sensor platform for Family Health Tracker."""
import logging
from datetime import datetime
import json
import os
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import TEMP_CELSIUS, CONF_NAME

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
    ATTR_TIMESTAMP,
    ATTR_HISTORY,
    MEDICATION_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Family Health Tracker sensor."""
    _LOGGER.debug("Setting up Family Health Tracker sensor platform")

    try:
        name = config_entry.data[CONF_NAME]
        members_str = config_entry.data[CONF_MEMBERS]
        _LOGGER.debug("Configuring sensors for members: %s", members_str)

        members = [member.strip() for member in members_str.split(",")]

        sensors = []
        for member in members:
            _LOGGER.debug("Creating sensor for member: %s", member)
            sensor = HealthTrackerSensor(hass, member, config_entry.entry_id)
            sensors.append(sensor)

        async_add_entities(sensors, True)
        _LOGGER.debug("Successfully added %d sensors", len(sensors))

    except Exception as ex:
        _LOGGER.error("Error setting up sensors: %s", str(ex))

class HealthTrackerSensor(SensorEntity):
    """Representation of a Health Tracker Sensor."""

    def __init__(self, hass: HomeAssistant, name: str, entry_id: str) -> None:
        """Initialize the sensor."""
        _LOGGER.debug("Initializing sensor for %s", name)

        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = None
        self._attributes = {
            ATTR_TEMPERATURE: None,
            ATTR_MEDICATION: None,
            ATTR_TIMESTAMP: None,
            ATTR_HISTORY: []
        }
        self._unique_id = f"{DOMAIN}_{name.lower()}"
        self._file_path = os.path.join(
            self._hass.config.path("custom_components", DOMAIN),
            f"data_{self._unique_id}.json"
        )
        _LOGGER.debug("Data file path: %s", self._file_path)
        self._load_data()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"Health Tracker {self._name}"

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def _load_data(self) -> None:
        """Load historical data from file."""
        _LOGGER.debug("Loading data for %s", self._name)
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r") as file:
                    data = json.load(file)
                    self._attributes[ATTR_HISTORY] = data.get(ATTR_HISTORY, [])
                    if self._attributes[ATTR_HISTORY]:
                        latest = self._attributes[ATTR_HISTORY][-1]
                        self._state = latest.get(ATTR_TEMPERATURE)
                        self._attributes[ATTR_TEMPERATURE] = latest.get(ATTR_TEMPERATURE)
                        self._attributes[ATTR_MEDICATION] = latest.get(ATTR_MEDICATION)
                        self._attributes[ATTR_TIMESTAMP] = latest.get(ATTR_TIMESTAMP)
                        _LOGGER.debug("Loaded %d history records", len(self._attributes[ATTR_HISTORY]))
            except Exception as error:
                _LOGGER.error("Error loading data for %s: %s", self._name, error)

    def _save_data(self) -> None:
        """Save data to file."""
        _LOGGER.debug("Saving data for %s", self._name)
        try:
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
            with open(self._file_path, "w") as file:
                json.dump({ATTR_HISTORY: self._attributes[ATTR_HISTORY]}, file)
            _LOGGER.debug("Successfully saved data")
        except Exception as error:
            _LOGGER.error("Error saving data for %s: %s", self._name, error)

    def add_measurement(self, temperature: float, medication: str) -> None:
        """Add a new measurement."""
        _LOGGER.debug("Adding measurement for %s: temp=%f, med=%s", 
                     self._name, temperature, medication)

        if medication not in MEDICATION_OPTIONS:
            _LOGGER.error("Invalid medication option: %s", medication)
            return

        timestamp = datetime.now().isoformat()
        measurement = {
            ATTR_TEMPERATURE: temperature,
            ATTR_MEDICATION: medication,
            ATTR_TIMESTAMP: timestamp
        }

        self._state = temperature
        self._attributes[ATTR_TEMPERATURE] = temperature
        self._attributes[ATTR_MEDICATION] = medication
        self._attributes[ATTR_TIMESTAMP] = timestamp
        self._attributes[ATTR_HISTORY].append(measurement)

        self._save_data()
        self.schedule_update_ha_state()
        _LOGGER.debug("Measurement added successfully")