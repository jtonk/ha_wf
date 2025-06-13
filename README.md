# Windfinder Home Assistant Integration

This repository contains a custom integration and Lovelace card to display wind conditions from Windfinder using a Node-RED backend.

## Installation

1. Copy this repository into your Home Assistant `config` directory so the structure looks like `custom_components/windfinder` and `www/windfinder-card.js`.
2. Restart Home Assistant.
3. Use HACS or the integrations page to add **Windfinder** and follow the setup flow to configure your location and Node-RED endpoint.
4. Add the `windfinder-card` to your dashboard and select the sensor entity.

## Development

The backend fetches data from the Node-RED endpoint specified during configuration. The frontend card displays speed, direction and gust values provided by the sensor entity.
