"""Constants for the Family Health Tracker integration."""

DOMAIN = "family_health_tracker"
VERSION = "1.0.0"

CONF_MEMBERS = "members"

# Medication options
MEDICATION_NONE = "none"
MEDICATION_PARACETAMOL = "paracetamol"
MEDICATION_IBUPROFEN = "ibuprofen"

MEDICATION_OPTIONS = [
    MEDICATION_NONE,
    MEDICATION_PARACETAMOL,
    MEDICATION_IBUPROFEN,
]

DEFAULT_NAME = "Health Tracker"

ATTR_TEMPERATURE = "temperature"
ATTR_MEDICATION = "medication"
ATTR_TIMESTAMP = "timestamp"
ATTR_HISTORY = "history"
