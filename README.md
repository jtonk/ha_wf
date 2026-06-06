# Windfinder Home Assistant Integration

A custom integration that fetches wind and weather information from [windfinder.com](https://www.windfinder.com) and exposes it as sensors in Home Assistant.

## Installation

### No HACS
1. Copy this repository to your `config/custom_components` directory so that the path becomes `custom_components/windfinder`.
2. Restart Home Assistant.
3. From the integrations page or via HACS, add **Windfinder** and provide your desired location. The location is normalised to lower case.

### With HACS
1. add a new custom repo, use https://github.com/jtonk/ha_wf/ repo and the integration category
2. search for Windfinder in HACS & install it
3. restart Home Assistant
4. From the integrations page or via HACS, add **Windfinder** and provide your desired location. The location is normalised to lower case.

The integration fetches once on startup or reload. After that it schedules the next refresh for 5 minutes after the earliest `next update` timestamp reported by the forecast or superforecast page. The sensor state is recalculated hourly from the fetched forecast data.

## Usage
For each configured location a sensor and a refresh button are created. The sensor's state reports the predicted wind speed in knots for the active forecast hour, preferring `superforecastdata` when available and falling back to `forecastdata`. The full forecast data and update timestamps are available in the sensor attributes.

The forecast attributes remain available on the live entity but are excluded
from recorder history. This prevents the large forecast arrays from exceeding
Home Assistant's recorder attribute-size limit and allows long-term wind-speed
statistics to be compiled reliably.

To trigger an immediate update you can call the `windfinder.refresh` service:

```yaml
service: windfinder.refresh
data:
  entity_id: sensor.windfinder_noordwijk
```

## Sensor Attributes
- `forecastdata` / `superforecastdata` – hourly forecast points with `datetime` and `tide_datetime` stored as UTC ISO timestamps.
- `forecast_generated` / `superforecast_generated` – last update timestamps reported by Windfinder, stored in UTC.
- `forecast_last_update` / `superforecast_last_update` – explicit aliases for the last update timestamps, stored in UTC.
- `forecast_next_update` / `superforecast_next_update` – next update timestamps reported by Windfinder, stored in UTC.
- `forecast_fetched` / `superforecast_fetched` – timestamps for when Home Assistant fetched the page, stored in UTC.
- `spot_name` – the name of the location returned by Windfinder.
- `spot_timezone` – the spot's IANA timezone identifier reported by Windfinder, for example `Europe/Amsterdam`.

Forecast measurements are rounded to practical display precision: wind,
temperature, rain, and wave period to one decimal; wave and tide heights to two
decimals; and directions, percentages, humidity, and pressure to whole numbers.
The sensor state is rounded to one decimal knot.

## License
MIT
