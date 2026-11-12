const css = `
:host {
  display: block;
  font-size: 11px;

}
.title-block {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  column-gap: 8px;
  row-gap: 6px;
  padding: 12px 16px 12px 16px;
}
.icon-title-block {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
}
.icon-title-block ha-icon {
  margin-right: 6px;
  vertical-align: middle;
  width: 32px;
  height: 32px;
  color: var(--state-icon-color, var(--primary-text-color));
}
.text-title-block {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  overflow: hidden;
}
.card-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--primary-text-color);
  line-height: 1.2;
  letter-spacing: 0.01em;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.subtitle {
  font-size: 12px;
  font-weight: 400;
  color: var(--secondary-text-color);
  margin: 0;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.controls {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: nowrap;
  justify-content: flex-end;
  min-width: 0;
  justify-self: end;
  overflow: hidden;
}
.control-group {
  display: flex;
  gap: 4px;
  align-items: center;
  min-width: 0;
}
.control-group[hidden] {
  display: none;
}
.control-group ha-switch {
  flex: 0 0 auto;
}
.footer {
  padding: 4px 12px;
  font-size: 9px;
  font-weight: 400;
  color: var(--secondary-text-color);
  text-align: right;
}
.footer.warning {
  color: var(--error-color);
  font-weight: bold;
}
/* Dates row */
.dates-row {
  display: table;
  table-layout: fixed;
  background: var(--card-background-color);
  top: 0;
  cursor: default;
  width: 100%;
  height: 70px;
}
.date-tab {
  display: table-cell;

  vertical-align: top;
  padding: 4px 0px 0px 0px;
  height: 100%;
  border-left: 1px solid var(--divider-color);
  border-right: 0px solid var(--divider-color);
  border-top: 0px solid var(--divider-color);
  border-bottom: 1px solid var(--divider-color);

  overflow: hidden;
  background: var(--card-background-color);
  transition: background-color 0.2s;
}
.date-tab:first-child {
  border-left: none;
}

.date-tab.active {
  background-color: var(--chip-background-color, #ff0000 );
  font-weight: bold;
  color: var(--primary-text-color);
  border-bottom: 1px solid var(--card-background-color);
}
.date-tab-inner {
  position: relative;
  height: 100%;
}

.date-label {
  position: absolute;
  font-size: 11px;
  color: var(--primary-text-color);
  top: 0;
  left: 0;
  right: 0;
  text-align: center;
  z-index: 2;
  padding: 4px;
}

.date-wind-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: -1px;
  text-align: center;
  z-index: 1;
  min-height: 4px;
  margin-top: 2px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 0px;
}
.wind-bar-segment {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column-reverse; /* stack from bottom up */
  align-items: stretch;
  margin-right: 1px;
}

.wind-bar-segment.alert::after{
  content: " ";
  background: red;
  position: absolute;
  width: 100%;
  height: 4px;
  z-index: 0;

}
.date-wind-bar-segment {
  display: inline-block;
  margin-right: 1px;
}

.date-gust-bar-segment {
  display: inline-block;
  margin-right: 1px;
}

/* Forecast table container */
.forecast-table {
  display: table;
  table-layout: fixed;
  width: 100%;
}

/* Header row */
.forecast-header {
  display: table-header-group;
  background: var(--card-background-color);
  color: var(--primary-text-color);
  font-size: 11px;
}
.forecast-cell {
  display: table-cell;
  padding: 2px;
  text-align: center;
  font-weight: 600;
  user-select: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  border-left: 1px solid var(--divider-color);
  border-right: 0px solid var(--divider-color);
  border-top: 0px solid var(--divider-color);
  border-bottom: 1px solid var(--divider-color);
  vertical-align: middle;
}

.forecast-cell.square {
  width: 36px;
}
.forecast-cell:first-child {
  border-left: none;
}

/* Data rows */
.forecast-body{
  display: table-row-group;
}
.forecast-row {
  display: table-row;
  font-size: 11px;
  color: var(--primary-text-color);
}

.forecast-row.night {
  background-color: var(--chip-background-color, #ff0000 );
  color: var(--primary-text-color);
}
ha-card.hide-night .forecast-row.night {
  display: none;
}
.forecast-cell-value {
  display: table-cell;
  padding: 2px;
  text-align: center;
  color: inherit;
  white-space: nowrap;
  border-left: 1px solid var(--divider-color);
  border-right: 0px solid var(--divider-color);
  border-top: 0px solid var(--divider-color);
  border-bottom: 1px solid var(--divider-color);
  vertical-align: middle;
}
.forecast-cell-value:first-child {
  border-left: none;
}
.forecast-cell-value:first-child.alert {
  border-left: 4px solid red;
}
.forecast-cell-value.current-hour {
  background-color: var(--chip-background-color, #ff0000 );
  font-weight: bold;
  color: var(--primary-text-color);
}
ha-icon.rotated {
  color: var(--primary-text-color);
  display: inline-block;
  transform-origin: center center;
  vertical-align: middle;
  width: 16px;
  height: 16px;
}

.toggle-label {
  font-size: 0.8rem;
  margin-left: 6px;
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 720px) {
  .title-block {
    column-gap: 6px;
    padding: 10px 12px;
  }
  .icon-title-block {
    min-width: 28px;
    min-height: 28px;
  }
  .icon-title-block ha-icon {
    margin-right: 4px;
    width: 28px;
    height: 28px;
  }
  .controls {
    gap: 6px;
  }
  .control-group {
    gap: 2px;
  }
  .card-title {
    font-size: 13px;
  }
  .subtitle {
    font-size: 11px;
  }
  .toggle-label {
    margin-left: 4px;
    max-width: 3.8em;
  }
}

`;
const FIXED_GRID_COLUMNS = 12;
const DEFAULT_GRID_ROWS = 8;
const GRID_ROW_PX = 56;
const GRID_GAP_PX = 8;
const GRID_STEP_PX = GRID_ROW_PX + GRID_GAP_PX;
const DEFAULT_TITLE = 'Kite Forecast';
const FORECAST_INTERVAL_MS = 3 * 60 * 60 * 1000;
const SUPERFORECAST_INTERVAL_MS = 60 * 60 * 1000;
const TIME_ZONE_ALIASES = {
  'America/Kralendijk': 'America/Curacao',
};
const WIND_SCALE_COLORS = [
  "#9700ff", "#6400ff", "#3200ff", "#0032ff", "#0064ff", "#0096ff", "#00c7ff",
  "#00e6f0", "#25c192", "#11d411", "#00e600", "#00fa00", "#b8ff61", "#fffe00",
  "#ffe100", "#ffc800", "#ffaf00", "#ff9600", "#e67d00", "#e66400", "#dc4a1d",
  "#c8321d", "#b4191d", "#aa001d", "#b40032", "#c80064", "#fe0096"
];

function stableSerialize(value) {
  if (Array.isArray(value)) {
    return `[${value.map(stableSerialize).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    const entries = Object.keys(value)
      .filter((key) => value[key] !== undefined)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableSerialize(value[key])}`);
    return `{${entries.join(',')}}`;
  }
  return JSON.stringify(value);
}

function normalizeAlertConfig(alert) {
  if (!alert) return undefined;

  const normalized = {
    angles: Array.isArray(alert.angles)
      ? alert.angles
        .map((range) => {
          const from = Number(range?.from);
          const to = Number(range?.to);
          return {
            ...(Number.isFinite(from) ? { from } : {}),
            ...(Number.isFinite(to) ? { to } : {}),
          };
        })
      : [],
  };

  const speedMin = Number(alert.speed_min);
  if (Number.isFinite(speedMin)) {
    normalized.speed_min = speedMin;
  }

  return normalized;
}

function normalizeCardConfig(config = {}) {
  const normalized = {
    ...config,
    show_night: config.show_night ?? false,
    default_source: config.default_source || 'forecastdata',
  };

  if (!normalized.title) {
    delete normalized.title;
  }

  const alert = normalizeAlertConfig(normalized.alert);
  if (alert) {
    normalized.alert = alert;
  } else {
    delete normalized.alert;
  }

  delete normalized.timezone;
  return normalized;
}

class HaWfCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("Entity is required");
    const normalizedConfig = normalizeCardConfig(config);
    const nextConfigKey = stableSerialize(normalizedConfig);
    if (this._configKey === nextConfigKey) {
      return;
    }

    const previousEntity = this.config?.entity;
    const previousDefaultSource = this._defaultSource;
    const previousAlertKey = stableSerialize(normalizeAlertConfig(this.config?.alert));
    const hadShell = !!this.querySelector('ha-card');

    this._configKey = nextConfigKey;
    this.config = normalizedConfig;
    this._alertConfig = normalizedConfig.alert || null;
    this._showNight = normalizedConfig.show_night;
    this._defaultSource = normalizedConfig.default_source;
    this._gridRows = this._gridRows || DEFAULT_GRID_ROWS;
    this._gridRowSyncFrame = this._gridRowSyncFrame || 0;

    if (!hadShell) {
      this._renderCardShell();
      this._bindCardEvents();
    }

    if (previousEntity !== normalizedConfig.entity) {
      this._spotTimeZone = undefined;
      this._selectedSource = null;
      this._lastStateObj = null;
      this._activeDay = null;
    } else if (previousDefaultSource !== this._defaultSource) {
      this._selectedSource = this._defaultSource;
    }

    this._syncCardShell();

    if (this._hass && (
      previousEntity !== normalizedConfig.entity
      || previousDefaultSource !== this._defaultSource
      || previousAlertKey !== stableSerialize(normalizeAlertConfig(this._alertConfig))
      || !hadShell
    )) {
      this._updateFromSelectedSource();
    } else {
      this._applyNightVisibility();
    }
  }

  _renderCardShell() {
    this.innerHTML = `
      <style>${css}</style>

      <ha-card>
          <div class="title-block">
            <div class="icon-title-block">
              <ha-icon id="refresh-icon" style="cursor:pointer" title="Refresh"></ha-icon>
            </div>
            <div class="text-title-block">
              <div class="card-title">${this._escapeHtml(this.config.title || DEFAULT_TITLE)}</div>
              <div class="subtitle" id="subtitle"></div>
            </div>
            <div class="controls" id="controls-container">
              <div class="control-group" id="night-control">
                <span class="toggle-label">Night</span>
                <ha-switch id="toggle-night" haptic title="Toggle night hours" aria-label="Toggle night hours" ${this._showNight ? 'checked' : ''}></ha-switch>
              </div>
              <div class="control-group" id="source-control">
                <span class="toggle-label">Superforecast</span>
                <ha-switch id="toggle-source" haptic title="Toggle forecast source (off=Forecast, on=Superforecast)" aria-label="Toggle forecast source" ${this._defaultSource === 'superforecastdata' ? 'checked' : ''}></ha-switch>
              </div>
            </div>
          </div>
        <div class="scroll-container">
          <div id="dates-row" class="dates-row"></div>
          <div class="forecast-table" id="forecast-table"></div>
        </div>
        <div class="footer" id="footer"></div>
      </ha-card>
    `;
    this._syncCardShell();
  }

  _syncCardShell() {
    const title = this.querySelector('.card-title');
    if (title) {
      title.textContent = this.config.title || DEFAULT_TITLE;
    }

    const nightToggle = this.querySelector("#toggle-night");
    if (nightToggle) {
      nightToggle.checked = this._showNight;
    }

    const sourceToggle = this.querySelector("#toggle-source");
    if (sourceToggle && !this._selectedSource) {
      sourceToggle.checked = this._defaultSource === 'superforecastdata';
    }
  }

  _bindCardEvents() {
    const refreshIcon = this.querySelector('#refresh-icon');
    if (refreshIcon) {
      refreshIcon.onclick = () => {
        if (this._hass) {
          this._hass.callService('windfinder', 'refresh', { entity_id: this.config.entity });
        }
      };
    }

    this.querySelector("#toggle-night").onchange = () => {
      this._showNight = this.querySelector("#toggle-night").checked;
      this._applyNightVisibility();
    };

    this.querySelector("#toggle-source").onchange = () => {
      const checked = this.querySelector("#toggle-source").checked;
      this._selectedSource = checked ? 'superforecastdata' : 'forecastdata';
      //this.querySelector("#source-label").textContent = checked ? 'Superforecast' : 'Forecast';
      this._updateFromSelectedSource();
    };
  }

  getGridOptions() {
    const rows = this._gridRows || DEFAULT_GRID_ROWS;
    return {
      columns: FIXED_GRID_COLUMNS,
      min_columns: FIXED_GRID_COLUMNS,
      max_columns: FIXED_GRID_COLUMNS,
      rows,
      min_rows: rows,
      max_rows: rows,
    };
  }

  disconnectedCallback() {
    if (this._gridRowSyncFrame) {
      cancelAnimationFrame(this._gridRowSyncFrame);
      this._gridRowSyncFrame = 0;
    }
  }

  set hass(hass) {
    this._hass = hass;
    const entity = this.config.entity;
    const stateObj = this._hass.states[entity];
    if (!stateObj) {
      this._lastStateObj = null;
      this._clearDisplay("Entity not found");
      return;
    }

    const refreshIcon = this.querySelector('#refresh-icon');
    if (refreshIcon) {
      const icon = stateObj.attributes.icon || 'mdi:windsock';
      refreshIcon.setAttribute('icon', icon);
    }

    if (stateObj === this._lastStateObj) return;
    this._lastStateObj = stateObj;
    this._updateFromSelectedSource();
  }

  _checkAlertCondition(speed, angleDeg, isNightHour = false) {
    const alert = this._alertConfig;
    if (!alert || !Array.isArray(alert.angles)) return false;
    if (isNightHour) return false;

    const minSpeed = this._toFiniteNumber(alert.speed_min) ?? Infinity;
    const speedValue = this._toFiniteNumber(speed);
    const angleValue = this._toFiniteNumber(angleDeg);
    if (speedValue == null || speedValue < minSpeed || angleValue == null) return false;

    const norm = v => ((v % 360) + 360) % 360;  // Normalize to 0–359

    const angle = norm(angleValue);

    return alert.angles.some(({ from, to }) => {
      const start = norm(from);
      const end = norm(to);

      if (start <= end) {
        return angle >= start && angle <= end;
      } else {
        // Wraparound case
        return angle >= start || angle <= end;
      }
    });
  }



  _updateFromSelectedSource() {
    if (!this._hass) return;
    const entity = this.config.entity;
    const stateObj = this._hass.states[entity];
    if (!stateObj) return;

    const controlsContainer = this.querySelector("#controls-container");
    const nightControl = this.querySelector("#night-control");
    const sourceControl = this.querySelector("#source-control");
    const sourceToggle = this.querySelector("#toggle-source");
    const hasSuper = Array.isArray(stateObj.attributes.superforecastdata);
    const hasForecast = Array.isArray(stateObj.attributes.forecastdata);
    const hasAnyForecast = hasSuper || hasForecast;
    const canToggleSource = hasSuper && hasForecast;

    if (controlsContainer) {
      controlsContainer.hidden = !hasAnyForecast;
    }
    if (nightControl) {
      nightControl.hidden = !hasAnyForecast;
    }
    if (sourceControl) {
      sourceControl.hidden = !canToggleSource;
    }
    let source = this._selectedSource;
    if (!source || !Array.isArray(stateObj.attributes[source])) {
      source = null;
    }
    if (!source) {
      if (this.config.default_source && Array.isArray(stateObj.attributes[this.config.default_source])) {
        source = this.config.default_source;
      } else if (hasForecast) {
        source = 'forecastdata';
      } else if (hasSuper) {
        source = 'superforecastdata';
      } else {
        this._clearDisplay("No forecast data available");
        return;
      }
    }

    this._selectedSource = source;
    if (sourceToggle) {
      sourceToggle.checked = source === 'superforecastdata';
    }

    const data = stateObj.attributes[source];
    if (!Array.isArray(data)) {
      this._clearDisplay("Forecast data is not an array");
      return;
    }
    if (data.length === 0) {
      this._clearDisplay("Forecast data is empty");
      return;
    }

    const subtitle = this.querySelector("#subtitle");
    const footer = this.querySelector("#footer");
    const datesRow = this.querySelector("#dates-row");
    const forecastTable = this.querySelector("#forecast-table");
    this._spotTimeZone = this._getSpotTimeZone(stateObj);
    const tzOpt = this._getLocaleTimeZoneOptions();
    const spot_name = stateObj.attributes.spot_name;
    const prefix = source === 'superforecastdata' ? 'superforecast' : 'forecast';
    const generated_at = stateObj.attributes[prefix + '_generated'];

    let generatedDate = new Date(generated_at);
    if (isNaN(generatedDate.getTime())) generatedDate = new Date();
    const now = new Date();
    const ageHours = (now - generatedDate) / 36e5;

    subtitle.textContent = `${spot_name || 'Unknown location'}`;

    const generatedStr = generatedDate.toLocaleDateString('en-GB', {
      weekday: 'short', day: 'numeric', month: 'short', ...tzOpt
    }) + ' ' + generatedDate.toLocaleTimeString('en-GB', {
      hour: '2-digit', minute: '2-digit', hour12: false, ...tzOpt
    });

    footer.textContent = `Generated ${generatedStr}`;
    footer.classList.toggle('warning', ageHours > 6);

    const getColorForWind = (speed) => {
      const value = this._toFiniteNumber(speed);
      if (value == null) return 'inherit';
      const index = Math.max(0, Math.min(WIND_SCALE_COLORS.length - 1, Math.floor(value / 2)));
      return WIND_SCALE_COLORS[index];
    };

    const getColorForTemperature = (temp) => {
      const value = this._toFiniteNumber(temp);
      if (value == null) return 'inherit';
      const index = Math.floor((value + 13) / 2);
      return WIND_SCALE_COLORS[Math.max(0, Math.min(WIND_SCALE_COLORS.length - 1, index))];
    };

    const sortedRows = data
      .filter((row) => {
        const dt = new Date(row.datetime);
        return !isNaN(dt.getTime());
      })
      .sort((left, right) => new Date(left.datetime) - new Date(right.datetime));
    const dayEntries = [];
    const dateFormatter = new Intl.DateTimeFormat('en-CA', {
      year: 'numeric', month: '2-digit', day: '2-digit', ...tzOpt,
    });

    for (const row of sortedRows) {
      const day = dateFormatter.format(new Date(row.datetime));
      const lastEntry = dayEntries[dayEntries.length - 1];
      if (lastEntry?.[0] === day) {
        lastEntry[1].push(row);
      } else {
        dayEntries.push([day, [row]]);
      }
    }
    if (!dayEntries.length) {
      this._clearDisplay("Forecast data contains no valid rows");
      return;
    }

    const groupedByDay = Object.fromEntries(dayEntries);

    if (!this._activeDay || !groupedByDay[this._activeDay]) {
      this._activeDay = dayEntries[0][0];
    }

    datesRow.innerHTML = dayEntries.map(([day, rows]) => {
      const activeClass = day === this._activeDay ? 'active' : '';
      const displayDay = this._formatDataDayLabel(rows[0]?.datetime);

      const windBars = rows.map(row => {
        const windSpeed = this._toFiniteNumber(row.wind_speed_kn);
        const gustSpeed = this._toFiniteNumber(row.wind_gust_kn);
        const colorWind = getColorForWind(row.wind_speed_kn);
        const colorGust = getColorForWind(row.wind_gust_kn);
        const gustDif = Math.max(0, (gustSpeed ?? 0) - (windSpeed ?? 0));
        const gustHeight = gustDif >= 1 ? 1 : 0;
        const gustMargin = gustDif >= 1 ? gustDif : 0;
        const windBarAlert = this._checkAlertCondition(row.wind_speed_kn, row.wind_direction_deg, row.night_hour);
        const windBarClass = `${windBarAlert ? 'alert' : ''}`;
        return `<div class="wind-bar-segment ${windBarClass}">
            <div class="date-wind-bar-segment" style="background:${colorWind};height:${Math.max(0, windSpeed ?? 0)}px;width:100%;display:inline-block;"></div>
            <div class="date-gust-bar-segment" style="background:${colorGust};height: ${gustHeight}px;margin-bottom:${gustMargin}px;width:100%;display:inline-block;"></div>
          </div>`;
      }).join('');

      return `
        <div class="date-tab ${activeClass}" data-day="${day}">
          <div class="date-tab-inner">
            <div class="date-label">${displayDay}</div>
            <div class="date-wind-bar" style="margin-top:2px;text-align:center;">${windBars}</div>
          </div>
        </div>
      `;
    }).join('');

    datesRow.querySelectorAll('.date-tab').forEach(tab => {
      tab.onclick = () => {
        this._activeDay = tab.dataset.day;
        datesRow.querySelector('.date-tab.active')?.classList.remove('active');
        tab.classList.add('active');
        this._renderSelectedDay();
      };
    });

    // Render forecast header
    forecastTable.innerHTML = `
      <div class="forecast-header">
        <div class="forecast-cell">Time</div>
        <div class="forecast-cell square">Wind<br>kn</div>
        <div class="forecast-cell square">Gust<br>kn</div>
        <div class="forecast-cell square">Wind<br>dir</div>
        <div class="forecast-cell square">Temp<br>°C</div>
        <div class="forecast-cell square">Cloud</div>
        <div class="forecast-cell">Rain<br>mm</div>
        <div class="forecast-cell">Pressure<br>hPa</div>
        <div class="forecast-cell square">Wave<br>dir</div>
        <div class="forecast-cell">Wave<br>m | sec</div>
      </div>
      <div class="forecast-body"></div>
    `;

    const body = forecastTable.querySelector('.forecast-body');
    this._renderSelectedDay = () => {
      const nowMs = Date.now();
      const activeRows = groupedByDay[this._activeDay];
      const fallbackIntervalMs = source === 'superforecastdata'
        ? SUPERFORECAST_INTERVAL_MS
        : FORECAST_INTERVAL_MS;

      const rowsHtml = activeRows.map((row, index) => {
        const nightClass = row.night_hour ? 'night' : '';
        const rotateDir = deg => ((deg + 180) % 360);
        const windSpeed = this._toFiniteNumber(row.wind_speed_kn);
        const gustSpeed = this._toFiniteNumber(row.wind_gust_kn);
        const windDirection = this._toFiniteNumber(row.wind_direction_deg);
        const temperature = this._toFiniteNumber(row.temperature_c);
        const cloudCover = this._toFiniteNumber(row.cloud_cover_pct);
        const rainAmount = this._toFiniteNumber(row.rain_mm);
        const pressure = this._toFiniteNumber(row.air_pressure_hpa);
        const waveDirection = this._toFiniteNumber(row.wave_direction_deg);
        const waveHeight = this._toFiniteNumber(row.wave_height_m);
        const waveInterval = this._toFiniteNumber(row.wave_interval_s);

        const windDirIcon = (windDirection != null)
          ? `<ha-icon icon="mdi:navigation" class="rotated" style="transform: rotate(${rotateDir(windDirection)}deg); --mdc-icon-size: 16px;"></ha-icon>`
          : '';

        const waveDirIcon = (waveDirection != null)
          ? `<ha-icon icon="mdi:navigation" class="rotated" style="transform: rotate(${rotateDir(waveDirection)}deg); --mdc-icon-size: 16px;" ></ha-icon>`
          : '';

        const dt = new Date(row.datetime);
        const isAlert = this._checkAlertCondition(row.wind_speed_kn, row.wind_direction_deg, row.night_hour);
        const timeStr = this._formatTimeLabel(dt);
        const rowStart = dt.getTime();
        const nextRow = activeRows[index + 1];
        const nextRowStart = nextRow ? new Date(nextRow.datetime).getTime() : NaN;
        const rowEnd = Number.isFinite(nextRowStart) && nextRowStart > rowStart
          ? nextRowStart
          : rowStart + fallbackIntervalMs;
        const isCurrentHour = nowMs >= rowStart && nowMs < rowEnd;

        const timeClasses = [isAlert ? 'alert' : '', isCurrentHour ? 'current-hour' : ''].filter(Boolean).join(' ');

        const getWeatherIcon = (cloudPct, rainMm, isNight) => {
          if (cloudPct == null) return "mdi:weather-cloudy";

          const rain = rainMm ?? 0;

          if (cloudPct <= 10) {
            return isNight ? "mdi:weather-night" : (rain > 0 ? "mdi:weather-partly-rainy" : "mdi:weather-sunny");
          }

          if (cloudPct <= 50) {
            if (rain > 0) return "mdi:weather-partly-rainy";
            return isNight ? "mdi:weather-night-partly-cloudy" : "mdi:weather-partly-cloudy";
          }

          if (rain > 5) return "mdi:weather-pouring";
          if (rain > 0.2) return "mdi:weather-rainy";

          return "mdi:weather-cloudy";
        };

        return `
          <div class="forecast-row ${nightClass}">
            <div class="forecast-cell-value ${timeClasses}">${timeStr}</div>

            ${(() => {
              const bg = getColorForWind(windSpeed);
              const fg = this._getContrastTextColor(bg);
              return `<div class="forecast-cell-value" style="background:${bg};color:${fg};">${this._formatNumber(windSpeed, 0)}</div>`;
            })()}

            ${(() => {
              const bg = getColorForWind(gustSpeed);
              const fg = this._getContrastTextColor(bg);
              return `<div class="forecast-cell-value" style="background:${bg};color:${fg};">${this._formatNumber(gustSpeed, 0)}</div>`;
            })()}


            <div class="forecast-cell-value icon">${windDirIcon}</div>

            ${(() => {
              const bg = getColorForTemperature(temperature);
              const fg = this._getContrastTextColor(bg);
              return `<div class="forecast-cell-value icon" style="background:${bg};color:${fg};">${this._formatNumber(temperature, 1)}</div>`;
            })()}

            <div class="forecast-cell-value icon">
                <ha-icon icon="${getWeatherIcon(cloudCover, rainAmount, row.night_hour)}" style="--mdc-icon-size: 16px;" title="${this._formatNumber(cloudCover, 0, '?')}% cloud, ${this._formatNumber(rainAmount, 1, '0.0')}mm rain"></ha-icon>
            </div>

            <div class="forecast-cell-value">${rainAmount > 0 ? this._formatNumber(rainAmount, 1) : '-'}</div>

            <div class="forecast-cell-value">${this._formatNumber(pressure, 0)}</div>
            <div class="forecast-cell-value icon">${waveDirIcon}</div>
            <div class="forecast-cell-value">${this._formatMeasurement(waveHeight, 1, 'm')}<br>${this._formatMeasurement(waveInterval, 0, ' sec')}</div>
          </div>
        `;
      }).join('');
      body.innerHTML = rowsHtml;

      // Apply night visibility toggle
      this._applyNightVisibility();
    };
    this._renderSelectedDay();
  }

  _getLocaleTimeZoneOptions() {
    return this._spotTimeZone ? { timeZone: this._spotTimeZone } : {};
  }

  _getSpotTimeZone(stateObj) {
    const attributes = stateObj?.attributes ?? {};
    const candidates = [
      attributes.spot_timezone,
      attributes.spotTimeZone,
      attributes['Spot timezone'],
    ];

    for (const candidate of candidates) {
      const timeZone = this._normalizeTimeZone(candidate);
      if (timeZone) {
        return timeZone;
      }
    }

    for (const [key, value] of Object.entries(attributes)) {
      const normalizedKey = key.toLowerCase().replace(/[\s_-]+/g, '');
      if (normalizedKey !== 'spottimezone') continue;

      const timeZone = this._normalizeTimeZone(value);
      if (timeZone) {
        return timeZone;
      }
    }

    return undefined;
  }

  _normalizeTimeZone(value) {
    if (typeof value !== 'string') return undefined;
    const timeZone = value.trim();
    if (!timeZone) return undefined;
    const normalized = timeZone.toLowerCase() === 'utc' ? 'UTC' : timeZone;

    const candidates = [normalized, TIME_ZONE_ALIASES[normalized]].filter(Boolean);
    for (const candidate of candidates) {
      try {
        Intl.DateTimeFormat('en-US', { timeZone: candidate });
        return candidate;
      } catch (_error) {
        continue;
      }
    }

    return undefined;
  }

  _formatDataDayLabel(value) {
    const parsedDate = new Date(value);
    if (isNaN(parsedDate.getTime())) {
      return '-';
    }
    return parsedDate.toLocaleDateString('en-GB', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      ...this._getLocaleTimeZoneOptions(),
    });
  }

  _formatTimeLabel(date) {
    return date.toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      ...this._getLocaleTimeZoneOptions(),
    });
  }

  _toFiniteNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  _formatNumber(value, digits = 0, fallback = '-') {
    return value == null ? fallback : value.toFixed(digits);
  }

  _formatMeasurement(value, digits, unit, fallback = '-') {
    return value == null ? fallback : `${value.toFixed(digits)}${unit}`;
  }

  _escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;');
  }



  _getContrastTextColor(color) {
    let r, g, b;

    if (color.startsWith('rgba') || color.startsWith('rgb')) {
      const match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (!match) return '#000';
      r = parseInt(match[1], 10);
      g = parseInt(match[2], 10);
      b = parseInt(match[3], 10);
    } else if (color.startsWith('#')) {
      const hex = color.slice(1);
      if (hex.length === 3) {
        r = parseInt(hex[0] + hex[0], 16);
        g = parseInt(hex[1] + hex[1], 16);
        b = parseInt(hex[2] + hex[2], 16);
      } else if (hex.length === 6) {
        r = parseInt(hex.slice(0, 2), 16);
        g = parseInt(hex.slice(2, 4), 16);
        b = parseInt(hex.slice(4, 6), 16);
      } else {
        return '#000';
      }
    } else {
      return '#000';
    }

    const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
    return luminance > 110 ? '#000000' : '#ffffff';
  }


  _applyNightVisibility() {
    this.querySelector('ha-card')?.classList.toggle('hide-night', !this._showNight);
    this._scheduleGridRowSync();
  }

  _scheduleGridRowSync() {
    if (this._gridRowSyncFrame) {
      cancelAnimationFrame(this._gridRowSyncFrame);
    }

    this._gridRowSyncFrame = requestAnimationFrame(() => {
      this._gridRowSyncFrame = 0;
      const card = this.querySelector('ha-card');
      if (!card) return;

      const nextRows = Math.max(1, Math.ceil((card.scrollHeight + GRID_GAP_PX) / GRID_STEP_PX));
      if (nextRows === this._gridRows) return;

      this._gridRows = nextRows;

      this.dispatchEvent(new Event('iron-resize', { bubbles: true, composed: true }));
    });
  }

  _clearDisplay(msg) {
    const subtitle = this.querySelector("#subtitle");
    const footer = this.querySelector("#footer");
    const datesRow = this.querySelector("#dates-row");
    const forecastTable = this.querySelector("#forecast-table");

    subtitle.textContent = msg;
    footer.textContent = '';
    footer.classList.remove('warning');
    datesRow.innerHTML = '';
    forecastTable.innerHTML = '';
    this._scheduleGridRowSync();
  }
}

if (!customElements.get('ha-wf-card')) {
  customElements.define('ha-wf-card', HaWfCard);
}

HaWfCard.getConfigElement = () => document.createElement('ha-wf-card-editor');
HaWfCard.getStubConfig = () => ({
  entity: '',
  title: '',
  show_night: false,
  default_source: 'forecastdata',
});

const editorCss = `
  :host {
    display: block;
  }
  .editor {
    display: grid;
    gap: 12px;
  }
  .section {
    display: grid;
    gap: 12px;
    padding: 16px 0 0;
    border-top: 1px solid var(--divider-color);
  }
  .section:first-child {
    padding-top: 0;
    border-top: 0;
  }
  .section-header {
    display: grid;
    gap: 4px;
    padding: 0 16px;
  }
  .section-title {
    font-size: 1rem;
    font-weight: 600;
  }
  .section-description {
    font-size: 13px;
    color: var(--secondary-text-color);
  }
  .field-stack {
    display: grid;
    gap: 16px;
    padding: 0 16px;
  }
  .field {
    display: grid;
    gap: 6px;
  }
  .field label,
  .toggle-row label,
  .angles-header {
    font-size: 13px;
    font-weight: 600;
  }
  ha-textfield,
  ha-form {
    width: 100%;
  }
  .switch-field {
    padding: 0 16px;
  }
  ha-formfield {
    display: block;
    --ha-formfield-label-font-size: 14px;
  }
  .alert-layout {
    display: grid;
    gap: 14px;
    padding: 0 16px 16px;
  }
  .angles-panel {
    display: grid;
    gap: 12px;
    min-width: 0;
  }
  .alert-top {
    display: grid;
    gap: 16px;
    grid-template-columns: minmax(0, 1fr) 180px;
    align-items: start;
  }
  .alert-preview {
    display: grid;
    justify-items: center;
    gap: 8px;
    padding-top: 6px;
  }
  .alert-circle {
    position: relative;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    border: 1px solid var(--divider-color);
    background:
      radial-gradient(circle at center, var(--card-background-color) 0 34px, transparent 35px),
      var(--alert-preview, conic-gradient(transparent 0deg 360deg));
  }
  .alert-circle::before {
    content: "";
    position: absolute;
    top: -6px;
    left: 50%;
    width: 2px;
    height: 14px;
    transform: translateX(-50%);
    background: var(--primary-text-color);
    border-radius: 999px;
  }
  .alert-caption {
    font-size: 12px;
    color: var(--secondary-text-color);
    text-align: center;
  }
  button {
    font: inherit;
    border: 1px solid var(--divider-color);
    border-radius: 10px;
    background: var(--card-background-color);
    color: var(--primary-text-color);
    padding: 8px 12px;
    cursor: pointer;
  }
  button.primary {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
    border-color: var(--primary-color);
  }
  .range-list {
    display: grid;
    gap: 10px;
  }
  .range-row {
    display: grid;
    gap: 10px;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto;
    align-items: end;
    padding: 12px;
    border: 1px solid var(--divider-color);
    border-radius: 12px;
    background: var(--card-background-color);
  }
  .range-summary {
    grid-column: 1 / -1;
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .remove-range {
    align-self: center;
    color: var(--error-color);
  }
  .field-hint {
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .empty-state {
    padding: 14px;
    border-radius: 14px;
    border: 1px dashed var(--divider-color);
    color: var(--secondary-text-color);
  }
  @media (max-width: 800px) {
    .alert-top {
      grid-template-columns: 1fr;
    }
    .range-row {
      grid-template-columns: 1fr;
    }
  }
`;

class HaWfCardEditor extends HTMLElement {
  setConfig(config) {
    const normalizedConfig = normalizeCardConfig(config);
    const nextConfigKey = stableSerialize(normalizedConfig);
    if (this._configKey === nextConfigKey) {
      return;
    }

    this._configKey = nextConfigKey;
    this._config = normalizedConfig;
    this._render();
  }

  set hass(hass) {
    const previousCanSelectSuperforecast = this._canSelectSuperforecast();
    this._hass = hass;
    const canSelectSuperforecast = this._canSelectSuperforecast();

    if (this._config?.default_source === 'superforecastdata' && !canSelectSuperforecast) {
      this._updateConfig({ default_source: 'forecastdata' }, { render: true });
      return;
    }

    this._setupEntityForm();

    if (this.shadowRoot && previousCanSelectSuperforecast !== canSelectSuperforecast) {
      this._render();
    }
  }

  connectedCallback() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._config) return;

    const alert = this._normalizeAlert(this._config.alert);
    const alertEnabled = !!alert;
    const canSelectSuperforecast = this._canSelectSuperforecast();

    this.shadowRoot.innerHTML = `
      <style>${editorCss}</style>
      <div class="editor">
        <section class="section">
          <div class="section-header">
            <div class="section-title">Card Setup</div>
            <div class="section-description">Select the Windfinder entity and the default display behavior.</div>
          </div>
          <div class="field-stack">
            <div class="field">
              <ha-form id="entity-form"></ha-form>
              <div class="field-hint">Search by entity id or friendly name.</div>
            </div>
            <div class="field">
              <label for="title">Title</label>
              <ha-textfield id="title" data-field="title" value="${this._escape(this._config.title ?? '')}" placeholder="Kite Forecast"></ha-textfield>
            </div>
            ${canSelectSuperforecast ? `
              <div class="field switch-field">
                <ha-formfield label="Superforecast by default">
                  <ha-switch id="default_source_switch" data-field="default_source_switch" ${this._config.default_source === 'superforecastdata' ? 'checked' : ''}></ha-switch>
                </ha-formfield>
                <div class="field-hint">Turn this off to start on the regular forecast.</div>
              </div>
            ` : ''}
            <div class="field switch-field">
              <ha-formfield label="Show night hours by default">
                <ha-switch id="show_night" data-field="show_night" ${this._config.show_night ? 'checked' : ''}></ha-switch>
              </ha-formfield>
              <div class="field-hint">Night rows stay available in the card toggle either way.</div>
            </div>
          </div>
        </section>

        <section class="section">
          <div class="section-header">
            <div class="section-title">Alert Highlighting</div>
            <div class="section-description">Highlight forecast periods when wind speed and direction match your preferred sailing window.</div>
          </div>
          <div class="field switch-field">
            <ha-formfield label="Enable alert highlighting">
              <ha-switch id="alert_enabled" ${alertEnabled ? 'checked' : ''}></ha-switch>
            </ha-formfield>
            <div class="field-hint">Alerts are limited to non-night hours in the card.</div>
          </div>
          ${alertEnabled ? this._renderAlertSection(alert) : ''}
        </section>
      </div>
    `;

    this._setupEntityForm();

    this.shadowRoot.querySelectorAll('ha-textfield').forEach((field) => {
      if (field.hasAttribute('value')) {
        field.value = field.getAttribute('value');
      }
    });

    this.shadowRoot.querySelectorAll('ha-switch').forEach((toggle) => {
      toggle.checked = toggle.hasAttribute('checked');
    });

    this._bindEvents();
  }

  _renderAlertSection(alert) {
    const ranges = alert.angles ?? [];
    return `
      <div class="alert-layout">
        <div class="alert-top">
          <div class="field">
            <label for="alert_speed_min">Minimum wind speed (kn)</label>
            <ha-textfield id="alert_speed_min" data-alert-field="speed_min" type="number" min="0" step="1" value="${Number.isFinite(alert.speed_min) ? alert.speed_min : ''}" placeholder="15"></ha-textfield>
            <div class="field-hint">Only rows at or above this wind speed are highlighted.</div>
          </div>
          <div class="alert-preview">
            <div class="alert-circle" style="--alert-preview: ${this._buildAlertPreview(ranges)};"></div>
            <div class="alert-caption">0°/360° is at the top. A range like 315° to 45° wraps around north.</div>
          </div>
        </div>
        <div class="angles-panel">
          <div class="angles-header">Direction ranges</div>
          <div class="field-hint">Use degrees where 0/360 is north, 90 east, 180 south, and 270 west.</div>
          ${ranges.length ? `
            <div class="range-list">
            ${ranges.map((range, index) => `
              <div class="range-row">
                <div class="field">
                  <label for="range_from_${index}">From</label>
                  <ha-textfield id="range_from_${index}" data-range-index="${index}" data-range-field="from" type="number" min="0" max="360" step="1" value="${this._escape(range.from ?? '')}"></ha-textfield>
                </div>
                <div class="field">
                  <label for="range_to_${index}">To</label>
                  <ha-textfield id="range_to_${index}" data-range-index="${index}" data-range-field="to" type="number" min="0" max="360" step="1" value="${this._escape(range.to ?? '')}"></ha-textfield>
                </div>
                <button type="button" class="remove-range" data-remove-range="${index}">Remove</button>
                <div class="range-summary">${this._describeRange(range)}</div>
              </div>
            `).join('')}
            </div>
          ` : `<div class="empty-state">No direction ranges configured yet.</div>`}
          <button type="button" class="primary" id="add-range">Add direction range</button>
          <div class="field-hint">${this._describeAlert(ranges, alert.speed_min)}</div>
        </div>
      </div>
    `;
  }

  _bindEvents() {
    this.shadowRoot.querySelectorAll('[data-field]').forEach((el) => {
      const eventName = 'change';
      el.addEventListener(eventName, (ev) => {
        let value;
        if (el.tagName === 'HA-SWITCH') {
          value = el.checked;
        } else {
          value = ev.detail?.value ?? el.value;
        }
        this._updateConfigValue(el.dataset.field, value);
      });
    });

    const alertToggle = this.shadowRoot.querySelector('#alert_enabled');
    if (alertToggle) {
      alertToggle.addEventListener('change', () => {
        this._updateConfig({
          alert: alertToggle.checked ? { speed_min: 15, angles: [] } : undefined,
        }, { render: true });
      });
    }

    const speedInput = this.shadowRoot.querySelector('[data-alert-field="speed_min"]');
    if (speedInput) {
      speedInput.addEventListener('change', () => {
        const nextAlert = this._normalizeAlert(this._config.alert) ?? { angles: [] };
        const value = speedInput.value === '' ? undefined : Number(speedInput.value);
        nextAlert.speed_min = Number.isFinite(value) ? value : undefined;
        this._updateConfig({ alert: this._compactAlert(nextAlert) }, { render: true });
      });
    }

    this.shadowRoot.querySelectorAll('[data-range-field]').forEach((input) => {
      input.addEventListener('change', () => {
        const index = Number(input.dataset.rangeIndex);
        const field = input.dataset.rangeField;
        const nextAlert = this._normalizeAlert(this._config.alert) ?? { angles: [] };
        const nextAngles = [...(nextAlert.angles ?? [])];
        const nextRange = { ...(nextAngles[index] ?? {}) };
        nextRange[field] = input.value === '' ? undefined : Number(input.value);
        nextAngles[index] = nextRange;
        nextAlert.angles = nextAngles;
        this._updateConfig({ alert: this._compactAlert(nextAlert) }, { render: true });
      });
    });

    this.shadowRoot.querySelectorAll('[data-remove-range]').forEach((button) => {
      button.addEventListener('click', () => {
        const index = Number(button.dataset.removeRange);
        const nextAlert = this._normalizeAlert(this._config.alert) ?? { angles: [] };
        nextAlert.angles = (nextAlert.angles ?? []).filter((_, i) => i !== index);
        this._updateConfig({ alert: this._compactAlert(nextAlert) }, { render: true });
      });
    });

    const addButton = this.shadowRoot.querySelector('#add-range');
    if (addButton) {
      addButton.addEventListener('click', () => {
        const nextAlert = this._normalizeAlert(this._config.alert) ?? { speed_min: 15, angles: [] };
        nextAlert.angles = [...(nextAlert.angles ?? []), { from: 0, to: 30 }];
        this._updateConfig({ alert: this._compactAlert(nextAlert) }, { render: true });
      });
    }
  }

  _setupEntityForm() {
    const form = this.shadowRoot?.querySelector('#entity-form');
    if (!form) return;

    form.hass = this._hass;
    const entity = this._config.entity ?? '';
    if ((form.data?.entity ?? '') !== entity) {
      form.data = { entity };
    }
    form.schema = [{ name: 'entity', required: true, selector: { entity: {} } }];
    form.computeLabel = (schema) => schema.name === 'entity' ? 'Entity' : schema.name;

    if (!this._onEntityFormChanged) {
      this._onEntityFormChanged = (ev) => {
        ev.stopPropagation();
        this._updateConfigValue('entity', ev.detail?.value?.entity);
      };
    }

    if (this._entityForm !== form) {
      this._entityForm?.removeEventListener('value-changed', this._onEntityFormChanged);
      form.addEventListener('value-changed', this._onEntityFormChanged);
      this._entityForm = form;
    }
  }

  _updateConfigValue(key, value) {
    const next = {};
    let render = false;
    if (key === 'title') {
      next[key] = value || undefined;
    } else if (key === 'entity') {
      next.entity = value;
      render = true;
      if (this._config.default_source === 'superforecastdata' && !this._canSelectSuperforecast(value)) {
        next.default_source = 'forecastdata';
      }
    } else if (key === 'default_source_switch') {
      next.default_source = value ? 'superforecastdata' : 'forecastdata';
    } else {
      next[key] = value;
    }
    this._updateConfig(next, { render });
  }

  _updateConfig(changes, options = {}) {
    const nextConfig = normalizeCardConfig({
      ...this._config,
      ...changes,
    });
    const nextConfigKey = stableSerialize(nextConfig);
    if (this._configKey === nextConfigKey) {
      return;
    }

    this._config = nextConfig;
    this._configKey = nextConfigKey;

    this.dispatchEvent(new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true,
    }));

    if (options.render) {
      this._render();
    }
  }

  _canSelectSuperforecast(entityId = this._config?.entity) {
    const attributes = this._hass?.states?.[entityId]?.attributes;
    return Array.isArray(attributes?.forecastdata) && Array.isArray(attributes?.superforecastdata);
  }

  _normalizeAlert(alert) {
    if (!alert) return null;
    return {
      speed_min: this._parseFiniteNumber(alert.speed_min) ?? undefined,
      angles: Array.isArray(alert.angles)
        ? alert.angles.map((range) => ({
          from: this._parseFiniteNumber(range?.from) ?? undefined,
          to: this._parseFiniteNumber(range?.to) ?? undefined,
        }))
        : [],
    };
  }

  _compactAlert(alert) {
    if (!alert) return undefined;
    const angles = (alert.angles ?? []).filter((range) => range.from != null && range.to != null);
    return {
      ...(Number.isFinite(alert.speed_min) ? { speed_min: alert.speed_min } : {}),
      angles,
    };
  }

  _describeAlert(ranges, speedMin) {
    const speedText = Number.isFinite(speedMin) ? `${speedMin}+ kn` : 'any wind speed';
    if (!ranges?.length) {
      return `Alerting enabled for ${speedText}, but no wind direction ranges are selected yet.`;
    }
    return `${speedText} from ${ranges.map((range) => this._formatRange(range)).join(', ')}.`;
  }

  _buildAlertPreview(ranges) {
    const segments = [];
    const normalized = [];

    (ranges ?? []).forEach((range) => {
      if (range.from == null || range.to == null) return;
      const from = this._normalizeDeg(range.from);
      const to = this._normalizeDeg(range.to);
      if (from <= to) {
        normalized.push([from, to]);
      } else {
        normalized.push([from, 360], [0, to]);
      }
    });

    if (!normalized.length) {
      return 'conic-gradient(color-mix(in srgb, var(--divider-color) 18%, transparent) 0deg 360deg)';
    }

    normalized.sort((a, b) => a[0] - b[0]);
    let cursor = 0;
    normalized.forEach(([start, end]) => {
      if (start > cursor) {
        segments.push(`color-mix(in srgb, var(--divider-color) 12%, transparent) ${cursor}deg ${start}deg`);
      }
      segments.push(`color-mix(in srgb, var(--accent-color, var(--primary-color)) 65%, transparent) ${start}deg ${end}deg`);
      cursor = Math.max(cursor, end);
    });
    if (cursor < 360) {
      segments.push(`color-mix(in srgb, var(--divider-color) 12%, transparent) ${cursor}deg 360deg`);
    }

    return `conic-gradient(${segments.join(', ')})`;
  }

  _formatRange(range) {
    return `${this._normalizeDeg(range.from)}° to ${this._normalizeDeg(range.to)}°`;
  }

  _describeRange(range) {
    if (range.from == null || range.to == null) {
      return 'Fill in both values to define the sector.';
    }
    const from = this._normalizeDeg(range.from);
    const to = this._normalizeDeg(range.to);
    if (from === to) {
      return `${from}° matches only that exact direction.`;
    }
    if (from > to) {
      return `${from}° to ${to}° wraps around north across 0°/360°.`;
    }
    return `${from}° to ${to}° stays within the standard clockwise range.`;
  }

  _normalizeDeg(value) {
    return ((Number(value) % 360) + 360) % 360;
  }

  _parseFiniteNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  _escape(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;');
  }
}

if (!customElements.get('ha-wf-card-editor')) {
  customElements.define('ha-wf-card-editor', HaWfCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.find((card) => card.type === 'ha-wf-card')) {
  window.customCards.push({
    type: 'ha-wf-card',
    name: 'Windfinder Card',
    description: 'Windfinder forecast card with visual alert configuration.',
  });
}
