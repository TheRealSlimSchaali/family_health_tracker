"""Constants for the Family Health Tracker integration."""

DOMAIN = "family_health_tracker"
VERSION = "0.3.5"

CONF_MEMBERS = "members"
CONF_MEDICATIONS = "medications"  # New configuration option

# Default medication library
DEFAULT_MEDICATIONS = {
    "none": {
        "name": "None",
        "label": "No medication given",
        "dosage": None,
        "interval_hours": None,
        "category": "none"
    },
    "ibuprofen_200": {
        "name": "Ibuprofen 200mg",
        "label": "Ibuprofen 200mg administered",
        "dosage": "200mg",
        "interval_hours": 6,
        "category": "nsaid"
    },
    "ibuprofen_400": {
        "name": "Ibuprofen 400mg",
        "label": "Ibuprofen 400mg administered",
        "dosage": "400mg",
        "interval_hours": 6,
        "category": "nsaid"
    },
    "paracetamol_500": {
        "name": "Paracetamol 500mg",
        "label": "Paracetamol 500mg administered",
        "dosage": "500mg",
        "interval_hours": 6,
        "category": "antipyretic"
    },
    "aspirin_500": {
        "name": "Aspirin 500mg",
        "label": "Aspirin 500mg administered",
        "dosage": "500mg",
        "interval_hours": 6,
        "category": "nsaid"
    },
    "other": {
        "name": "Other",
        "label": "Other medication administered",
        "dosage": None,
        "interval_hours": None,
        "category": "other"
    }
}

# Configuration schema for medications
MEDICATION_SCHEMA = {
    "name": str,
    "label": str,
    "dosage": str,
    "interval_hours": int,
    "category": str
}

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

# Attributes
ATTR_TEMPERATURE = "temperature"
ATTR_MEDICATION = "medication"
ATTR_DOSAGE = "dosage"
ATTR_INTERVAL = "interval_hours"
ATTR_CATEGORY = "category"

DEFAULT_NAME = "Health Tracker"

# Helper functions to work with medications
def get_medication_options(medications=None):
    """Get medication options in the format needed for select entity."""
    meds = medications or DEFAULT_MEDICATIONS
    return [
        {"value": med_id, "label": med_info["label"]}
        for med_id, med_info in meds.items()
    ]

def get_medication_values(medications=None):
    """Get list of valid medication values."""
    meds = medications or DEFAULT_MEDICATIONS
    return list(meds.keys())