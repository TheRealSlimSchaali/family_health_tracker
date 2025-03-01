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
    MEDICATION_OPTIONS,
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
            sw_version="1.0",
            via_device=(DOMAIN, config_entry.entry_id),
        )

        # Create sensors
        temp_sensor = TemperatureSensor(hass, member, device_info, config_entry.entry_id)
        med_sensor = MedicationSensor(hass, member, device_info, config_entry.entry_id)
        entities.extend([temp_sensor, med_sensor])

        # Store sensor references for service calls
        entity_id_temp = f"sensor.{member_lower}_temperature"
        entity_id_med = f"sensor.{member_lower}_medication"

        hass.data[DOMAIN][config_entry.entry_id][entity_id_temp] = temp_sensor
        hass.data[DOMAIN][config_entry.entry_id][entity_id_med] = med_sensor

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
        
        # Make sure device info is properly set
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{name.lower()}")},
            name=name,
            manufacturer="Family Health Tracker",
            model="Health Monitor",
            sw_version="1.0",
            via_device=(DOMAIN, entry_id),
        )

        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_temperature"
        self._attr_name = "Temperature"

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

class MedicationSensor(SensorEntity):
    """Medication sensor for a family member."""

    def __init__(self, hass: HomeAssistant, name: str, device_info: DeviceInfo, entry_id: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._entry_id = entry_id
        self._state = "none"
        self._last_updated = None

        # Make sure device info is properly set
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{name.lower()}")},
            name=name,
            manufacturer="Family Health Tracker",
            model="Health Monitor",
            sw_version="1.0",
            via_device=(DOMAIN, entry_id),
        )

        self._attr_unique_id = f"{self._entry_id}_{name.lower()}_medication"
        self._attr_name = "Medication"

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
        return self._attributes

    async def update_medication(self, medication: str) -> None:
        """Update medication status."""
        self._state = medication
        self._last_updated = datetime.now().isoformat()
        self._attributes["last_medication"] = medication
        self._attributes["last_updated"] = self._last_updated
        self.async_schedule_update_ha_state()