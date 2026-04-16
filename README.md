# Windfinder Home Assistant Integration

A custom integration that fetches wind and weather information from [windfinder.com](https://www.windfinder.com) and exposes it as sensors in Home Assistant.
The plugin is intended to be used with https://github.com/jtonk/ha_wf_card/

## Installation

### No HACS
1. Copy this repository to your `config/custom_components` directory so that the path becomes `custom_components/windfinder`.
2. Restart Home Assistant.
3. From the integrations page or via HACS, add **Windfinder** and provide your desired location. The location is normalised to lower case.
4. The bundled `ha_wf_card` frontend module is served automatically by the integration, so no separate card repository or Lovelace resource entry is required.

### With HACS
1. add a new custom repo, use https://github.com/jtonk/ha_wf/ repo and the integration category
2. search for Windfinder in HACS & install it
3. restart Home Assistant
4. From the integrations page or via HACS, add **Windfinder** and provide your desired location. The location is normalised to lower case.

The integration fetches once on startup or reload. After that it schedules the next refresh for 5 minutes after the earliest `next update` timestamp reported by the forecast or superforecast page.

## Usage
For each configured location a sensor and a refresh button are created. The sensor's state indicates when the latest forecast was generated, while the full forecast data is available in the sensor attributes.

The included custom card is available as `type: custom:ha-wf-card` once the integration is loaded.

If you also develop the card in a separate checkout, refresh the bundled copy with:

```sh
./scripts/sync_ha_wf_card.sh
```

By default this reads from `../ha_wf_card/ha_wf_card.js`. You can also pass an explicit source path:

```sh
./scripts/sync_ha_wf_card.sh /path/to/ha_wf_card.js
```

To trigger an immediate update you can call the `windfinder.refresh` service:

```yaml
service: windfinder.refresh
data:
  entity_id: sensor.windfinder_noordwijk
```

Example dashboard card:

```yaml
type: custom:ha-wf-card
entity: sensor.windfinder_noordwijk
title: Noordwijk
show_night: false
default_source: forecastdata
timezone: Europe/Amsterdam
```

## Sensor Attributes
- `forecastdata` / `superforecastdata` – hourly forecast points.
- `forecast_generated` / `superforecast_generated` – last update timestamps reported by Windfinder.
- `forecast_last_update` / `superforecast_last_update` – explicit aliases for the last update timestamps.
- `forecast_next_update` / `superforecast_next_update` – next update timestamps reported by Windfinder.
- `forecast_fetched` / `superforecast_fetched` – timestamps for when Home Assistant fetched the page.
- `spot_name` – the name of the location returned by Windfinder.
- `spot_timezone` – the location timezone reported by Windfinder.
