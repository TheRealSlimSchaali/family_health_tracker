"""Constants for the Family Health Tracker integration."""

DOMAIN = "family_health_tracker"
VERSION = "0.3.5"

CONF_MEMBERS = "members"

# Medication values
MEDICATION_NONE = "none"
MEDICATION_PARACETAMOL = "paracetamol"
MEDICATION_IBUPROFEN = "ibuprofen"
MEDICATION_ASPIRIN = "aspirin"
MEDICATION_OTHER = "other"

# Medication options with labels
MEDICATION_OPTIONS = [
    {"value": MEDICATION_NONE, "label": "No medication given"},
    {"value": MEDICATION_PARACETAMOL, "label": "Paracetamol administered"},
    {"value": MEDICATION_IBUPROFEN, "label": "Ibuprofen administered"},
    {"value": MEDICATION_ASPIRIN, "label": "Aspirin administered"},
    {"value": MEDICATION_OTHER, "label": "Other medication administered"},
]

# List of just the values for validation
MEDICATION_VALUES = [opt["value"] for opt in MEDICATION_OPTIONS]

DEFAULT_NAME = "Health Tracker"

ATTR_TEMPERATURE = "temperature"
ATTR_MEDICATION = "medication"

# Temperature level ranges (in °C)
TEMP_LEVELS = {
    "low": {"min": 0, "max": 35.9},
    "normal": {"min": 36.0, "max": 37.2},
    "elevated": {"min": 37.3, "max": 38.0},
    "medium": {"min": 38.1, "max": 39.0},
    "high": {"min": 39.1, "max": 40.0},
    "very_high": {"min": 40.1, "max": 43.0},
}

# Default config
DEFAULT_TEMP_LEVELS = TEMP_LEVELS.copy()