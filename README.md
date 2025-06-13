# Windfinder Home Assistant Integration

This repository contains a custom integration that displays wind conditions from Windfinder. Data is fetched directly from windfinder.com.

## Installation

1. Copy this repository into your Home Assistant `config` directory so the structure looks like `custom_components/windfinder`.
2. Restart Home Assistant.
3. Use HACS or the integrations page to add **Windfinder** and follow the setup flow to configure your location.

## Development

The backend fetches data directly from windfinder.com based on the configured
location. Each configured location creates a device with a single sensor named
after the location (for example `sensor.hawf_noordwijk`). The sensor's state is
the timestamp of the last update reported on Windfinder. Forecast data and
current conditions are stored in the sensor's attributes for further use.
