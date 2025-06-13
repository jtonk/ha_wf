# Windfinder Home Assistant Integration

This repository contains a custom integration and Lovelace card to display wind conditions from Windfinder. Data is fetched directly from windfinder.com.

## Installation

1. Copy this repository into your Home Assistant `config` directory so the structure looks like `custom_components/windfinder` and `www/windfinder-card.js`.
2. Restart Home Assistant.
3. Use HACS or the integrations page to add **Windfinder** and follow the setup flow to configure your location.
4. Add the `windfinder-card` to your dashboard and select the sensor entity.

## Development

The backend fetches data directly from windfinder.com based on the configured location. The frontend card displays speed, direction and gust values provided by the sensor entity. Forecast data is exposed as attributes on the sensor for further use.
