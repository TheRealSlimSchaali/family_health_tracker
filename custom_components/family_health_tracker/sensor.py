"""Sensor platform for Family Health Tracker."""
import logging
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
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Family Health Tracker sensor."""
    name = config_entry.data[CONF_NAME]
    members_str = config_entry.data[CONF_MEMBERS]
    members = [member.strip() for member in members_str.split(",")]

    sensors = []
    for member in members:
        sensor = HealthTrackerSensor(member)
        sensors.append(sensor)

    async_add_entities(sensors, True)

class HealthTrackerSensor(SensorEntity):
    """Representation of a Health Tracker Sensor."""

    def __init__(self, name: str) -> None:
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._attributes = {
            ATTR_TEMPERATURE: None,
        }
        self._unique_id = f"{DOMAIN}_{name.lower()}"

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

    def add_measurement(self, temperature: float) -> None:
        """Add a new measurement."""
        self._state = temperature
        self._attributes[ATTR_TEMPERATURE] = temperature
        self.schedule_update_ha_state()