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
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME, UnitOfTemperature

from .const import (
    DOMAIN,
    CONF_MEMBERS,
    ATTR_TEMPERATURE,
    ATTR_MEDICATION,
    VERSION,
    TEMP_LEVELS,
    DEFAULT_MEDICATIONS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Family Health Tracker sensor."""
    _LOGGER.debug("Setting up sensors for config entry: %s", config_entry.data)

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

        temp_sensor = TemperatureSensor(hass, member, device_info, config_entry.entry_id)
        med_sensor = MedicationSensor(hass, member, device_info, config_entry.entry_id)
        duration_sensor = LastMedicationDurationSensor(hass, member, device_info, config_entry.entry_id)
        level_sensor = TemperatureLevelSensor(hass, member, device_info, config_entry.entry_id)
        entities.extend([temp_sensor, med_sensor, duration_sensor, level_sensor])

        # Store sensor references
        entity_id_temp = f"sensor.temperature_{member_lower}"
        entity_id_med = f"sensor.medication_{member_lower}"
        entity_id_duration = f"sensor.medication_duration_{member_lower}"
        entity_id_level = f"sensor.temperature_level_{member_lower}"

        hass.data[DOMAIN][config_entry.entry_id][entity_id_temp] = temp_sensor
        hass.data[DOMAIN][config_entry.entry_id][entity_id_med] = med_sensor
        hass.data[DOMAIN][config_entry.entry_id][entity_id_duration] = duration_sensor
        hass.data[DOMAIN][config_entry.entry_id][entity_id_level] = level_sensor

    async_add_entities(entities, True)

class TemperatureSensor(SensorEntity):
    """Temperature sensor for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = None
        self._last_updated = None
        
        self._attr_device_info = device_info
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_temperature"
        self.entity_id = f"sensor.temperature_{name.lower()}"
        self._attr_name = f"{name} Temperature"

        self._attributes = {
            "last_measurement": None,
            "last_updated": None
        }

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    async def update_temperature(self, temperature: float) -> None:
        """Update temperature measurement."""
        self._state = temperature
        self._last_updated = datetime.now().isoformat()
        self._attributes["last_measurement"] = temperature
        self._attributes["last_updated"] = self._last_updated
        self.async_schedule_update_ha_state()

        # Update the level sensor
        name_lower = self._name.lower()
        level_sensor_id = f"sensor.temperature_level_{name_lower}"
        level_sensor = self._hass.data[DOMAIN][self._entry_id].get(level_sensor_id)
        if level_sensor:
            await level_sensor.update_temperature(temperature)

class MedicationSensor(SensorEntity):
    """Medication sensor for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = "none"
        self._last_updated = None

        self._attr_device_info = device_info
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_medication"
        self.entity_id = f"sensor.medication_{name.lower()}"
        self._attr_name = f"{name} Medication"

        self._attributes = {
            "last_medication": None,
            "last_updated": None
        }

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attributes = self._attributes.copy()
        if self._state != "none":
            med_info = DEFAULT_MEDICATIONS.get(self._state, {})
            attributes.update({
                "dosage": med_info.get("dosage"),
                "interval_hours": med_info.get("interval_hours"),
                "category": med_info.get("category")
            })
        return attributes

    async def update_medication(self, medication: str) -> None:
        """Update medication status."""
        _LOGGER.debug("Updating medication for %s to %s", self._name, medication)
        self._state = medication
        self._last_updated = datetime.now().isoformat()
        self._attributes["last_medication"] = medication
        self._attributes["last_updated"] = self._last_updated
        self.async_schedule_update_ha_state()

        # Update the duration sensor
        name_lower = self._name.lower()
        duration_sensor_id = f"sensor.medication_duration_{name_lower}"
        duration_sensor = self._hass.data[DOMAIN][self._entry_id].get(duration_sensor_id)
        if duration_sensor:
            _LOGGER.debug("Found duration sensor, updating time")
            await duration_sensor.update_medication_time(medication)
        else:
            _LOGGER.warning("Could not find duration sensor: %s", duration_sensor_id)

class LastMedicationDurationSensor(SensorEntity):
    """Sensor tracking duration since last medication."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = None
        self._last_medication_time = None

        self._attr_device_info = device_info
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = "h"  # hours
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_medication_duration"
        self.entity_id = f"sensor.medication_duration_{name.lower()}"
        self._attr_name = f"{name} Time Since Medication"
        self._attr_translation_key = "medication_duration"

    @property
    def native_value(self) -> float | None:
        """Return the duration in hours."""
        if self._last_medication_time is None:
            return None
        now = datetime.now()
        duration = now - self._last_medication_time
        return round(duration.total_seconds() / 3600, 1)  # Convert to hours with 1 decimal

    async def update_medication_time(self, medication: str) -> None:
        """Update the last medication time."""
        _LOGGER.debug(
            "Updating medication time for %s. Medication: %s, Current time: %s",
            self._name,
            medication,
            datetime.now()
        )
        if medication != "none":  # Use string literal instead of constant
            self._last_medication_time = datetime.now()
            _LOGGER.debug("Updated last medication time to: %s", self._last_medication_time)
            self.async_schedule_update_ha_state()
        else:
            _LOGGER.debug("Skipping update for 'none' medication")

class TemperatureLevelSensor(SensorEntity):
    """Temperature level sensor for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = None
        self._current_temp = None
        
        self._attr_device_info = device_info
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_temperature_level"
        self.entity_id = f"sensor.temperature_level_{name.lower()}"
        self._attr_name = f"{name} Temperature Level"
        self._attr_translation_key = "temperature_level"

        # Get custom ranges from config if available
        self._temp_levels = TEMP_LEVELS
        if hass.data.get(DOMAIN, {}).get("temp_levels"):
            self._temp_levels = hass.data[DOMAIN]["temp_levels"]

    @property
    def state(self) -> str | None:
        """Return the current temperature level."""
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return {
            "temperature": self._current_temp,
            "ranges": self._temp_levels
        }

    def _get_level(self, temperature: float) -> str:
        """Determine temperature level based on current ranges."""
        for level, range_data in self._temp_levels.items():
            if range_data["min"] <= temperature <= range_data["max"]:
                return level
        return "unknown"

    async def update_temperature(self, temperature: float) -> None:
        """Update temperature level."""
        self._current_temp = temperature
        self._state = self._get_level(temperature)
        self.async_schedule_update_ha_state()