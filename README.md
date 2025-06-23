# Windfinder Home Assistant Integration

A custom integration that fetches wind and weather information from [windfinder.com](https://www.windfinder.com) and exposes it as sensors in Home Assistant.

## Installation
1. Copy this repository to your `config/custom_components` directory so that the path becomes `custom_components/windfinder`.
2. Restart Home Assistant.
3. From the integrations page or via HACS, add **Windfinder** and provide your desired location. The location is normalised to lower case.

The integration refreshes every 30 minutes by default. You can change the interval from the integration options.

## Usage
For each configured location a sensor and a refresh button are created. The sensor's state indicates when the latest forecast was generated, while the full forecast data is available in the sensor attributes.

To trigger an immediate update you can call the `windfinder.refresh` service:

```yaml
service: windfinder.refresh
data:
  entity_id: sensor.windfinder_noordwijk
```

## Sensor Attributes
- `forecastdata` / `superforecastdata` – hourly forecast points.
- `forecast_generated` / `forecast_fetched` – timestamps for the regular forecast.
- `superforecast_generated` / `superforecast_fetched` – timestamps for the superforecast.
- `spot_name` – the name of the location returned by Windfinder.
