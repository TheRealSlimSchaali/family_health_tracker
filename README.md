# Family Health Tracker for Home Assistant

A Home Assistant custom integration for tracking family members' temperature and medication data.

## Features

- Track temperature measurements for multiple family members
- Record medication administration (Paracetamol/Ibuprofen)
- Store historical data with timestamps
- Easy configuration through Home Assistant UI

## Installation

### HACS Installation

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Add"
7. Find "Family Health Tracker" in the integration list and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/family_health_tracker` directory to your Home Assistant's custom_components directory
2. Restart Home Assistant

## Configuration

1. Go to Configuration > Integrations
2. Click the "+ ADD INTEGRATION" button
3. Search for "Family Health Tracker"
4. Enter the required information:
   - Name: A name for the integration
   - Family Members: Comma-separated list of family members to track

## Usage

Each family member will have their own sensor entity. You can:

1. Record temperature measurements
2. Track medication administration
3. View historical data

### Service Calls

To add a new measurement, call the following service:

```yaml
service: family_health_tracker.add_measurement
data:
  name: "John"
  temperature: 37.5
  medication: "paracetamol"  # Options: "none", "paracetamol", "ibuprofen"
