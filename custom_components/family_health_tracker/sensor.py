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
    _LOGGER.debug("BEGIN async_setup_entry for sensor platform")
    _LOGGER.debug("Config entry data: %s", config_entry.data)

    try:
        name = config_entry.data[CONF_NAME]
        members_str = config_entry.data[CONF_MEMBERS]
        _LOGGER.debug("Processing configuration - name: %s, members: %s", name, members_str)

        members = [member.strip() for member in members_str.split(",")]
        _LOGGER.debug("Parsed member list: %s", members)

        sensors = []
        if config_entry.entry_id not in hass.data[DOMAIN]:
            hass.data[DOMAIN][config_entry.entry_id] = {}

        for member in members:
            try:
                _LOGGER.debug("Creating sensor for member: %s", member)
                sensor = HealthTrackerSensor(hass, member, config_entry.entry_id)
                sensors.append(sensor)
                # Store sensor object reference
                entity_id = f"sensor.health_tracker_{member.lower()}"
                hass.data[DOMAIN][config_entry.entry_id][entity_id] = sensor
                _LOGGER.debug("Successfully created sensor for: %s", member)
            except Exception as sensor_ex:
                _LOGGER.error("Failed to create sensor for %s: %s", member, str(sensor_ex), exc_info=True)
                raise

        _LOGGER.debug("Adding %d sensors to Home Assistant", len(sensors))
        async_add_entities(sensors, True)
        _LOGGER.debug("END async_setup_entry - Successfully added all sensors")

    except Exception as ex:
        _LOGGER.error("ERROR in async_setup_entry: %s", str(ex), exc_info=True)
        raise

class HealthTrackerSensor(SensorEntity):
    """Representation of a Health Tracker Sensor."""

    def __init__(self, hass: HomeAssistant, name: str, entry_id: str) -> None:
        """Initialize the sensor."""
        _LOGGER.debug("BEGIN initializing sensor for: %s", name)

        try:
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

            # Ensure the storage directory exists
            storage_dir = self._hass.config.path("custom_components", DOMAIN)
            _LOGGER.debug("Storage directory path: %s", storage_dir)
            os.makedirs(storage_dir, exist_ok=True)

            self._file_path = os.path.join(storage_dir, f"data_{self._unique_id}.json")
            _LOGGER.debug("Data file path: %s", self._file_path)

            self._load_data()
            _LOGGER.debug("END initializing sensor - Completed successfully")

        except Exception as ex:
            _LOGGER.error("ERROR initializing sensor for %s: %s", name, str(ex), exc_info=True)
            raise

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
        _LOGGER.debug("BEGIN loading data for: %s", self._name)
        _LOGGER.debug("Loading from file: %s", self._file_path)

        try:
            if os.path.exists(self._file_path):
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
            else:
                _LOGGER.debug("No existing data file found")

            _LOGGER.debug("END loading data - Completed successfully")

        except Exception as error:
            _LOGGER.error("ERROR loading data for %s: %s", self._name, str(error), exc_info=True)
            raise

    def _save_data(self) -> None:
        """Save data to file."""
        _LOGGER.debug("BEGIN saving data for: %s", self._name)
        _LOGGER.debug("Saving to file: %s", self._file_path)

        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)

            with open(self._file_path, "w") as file:
                json.dump({ATTR_HISTORY: self._attributes[ATTR_HISTORY]}, file)
            _LOGGER.debug("END saving data - Completed successfully")

        except Exception as error:
            _LOGGER.error("ERROR saving data for %s: %s", self._name, str(error), exc_info=True)
            raise

    def add_measurement(self, temperature: float, medication: str) -> None:
        """Add a new measurement."""
        _LOGGER.debug("BEGIN adding measurement for %s - temp: %f, medication: %s", 
                     self._name, temperature, medication)

        try:
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
            _LOGGER.debug("END adding measurement - Completed successfully")

        except Exception as error:
            _LOGGER.error("ERROR adding measurement for %s: %s", self._name, str(error), exc_info=True)
            raise