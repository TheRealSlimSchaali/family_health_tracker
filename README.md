# Family Health Tracker for Home Assistant

A Home Assistant custom integration for tracking family members' temperature and medication data.

## Features

- Track temperature measurements for multiple family members
- Record medication administration (Paracetamol/Ibuprofen)
- Timestamp tracking for all measurements
- Individual entities for temperature and medication
- Easy configuration through Home Assistant UI

## Installation

### Development Installation

1. Clone this repository
2. Copy the `custom_components/family_health_tracker` directory to your Home Assistant's custom_components directory
3. Restart Home Assistant
4. Add the integration through UI (Configuration -> Integrations -> Add Integration)

## Configuration

1. Go to Configuration > Integrations
2. Click the "+ ADD INTEGRATION" button
3. Search for "Family Health Tracker"
4. Enter the required information:
   - Name: A name for the integration
   - Family Members: Comma-separated list of family members to track

## Usage

Each family member will have two sensor entities:
1. Temperature sensor: Shows the latest temperature measurement with timestamp
2. Medication sensor: Shows the latest medication administered with timestamp

### Service Calls

To add a new measurement, call the following service:

```yaml
service: family_health_tracker.add_measurement
data:
  name: "John"
  temperature: 37.5
  medication: "none"  # Options: "none", "paracetamol", "ibuprofen"
```

### Supported Medication Options

- none
- paracetamol
- ibuprofen

## Development

This integration was developed for use with Home Assistant. To set up a development environment:

1. Set up Home Assistant development container
2. Copy the custom component to the appropriate directory
3. Configure Home Assistant with the basic configuration provided in `test_config.yaml`
4. Test the integration through the UI and service calls