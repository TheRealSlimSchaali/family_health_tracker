"""Constants for the Family Health Tracker integration."""

DOMAIN = "family_health_tracker"
VERSION = "0.3.5"

CONF_MEMBERS = "members"
CONF_MEDICATIONS = "medications"

# Default medication library (only 'none' option)
DEFAULT_MEDICATIONS = {
    "none": {
        "name": "None",
        "label": "No medication given",
        "dosage": None,
        "interval_hours": None,
        "category": "none"
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
def get_medication_options(user_medications=None):
    """Get medication options in the format needed for select entity."""
    # Start with default medications
    meds = DEFAULT_MEDICATIONS.copy()
    
    # Add user medications if any
    if user_medications:
        meds.update(user_medications)
    
    return [
        {"value": med_id, "label": med_info["label"]}
        for med_id, med_info in meds.items()
    ]

def get_medication_values(user_medications=None):
    """Get list of valid medication values."""
    # Start with default medications
    meds = DEFAULT_MEDICATIONS.copy()
    
    # Add user medications if any
    if user_medications:
        meds.update(user_medications)
    
    return list(meds.keys())

def get_combined_medications(user_medications=None):
    """Get combined dictionary of default and user medications."""
    meds = DEFAULT_MEDICATIONS.copy()
    if user_medications:
        meds.update(user_medications)
    return meds