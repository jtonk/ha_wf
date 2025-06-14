class KiteForecastCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("Entity is required");
    this.config = config;
    this._showNight = config.show_night ?? false;
    this._defaultSource = config.default_source || 'forecastdata';
    this._selectedSource = null;
    this._lastDataString = null;
    this._lastSource = null;
    this._activeDay = null;

    this.innerHTML = `
      <style>
        :host {
          display: block;
          font-size: 11px;

        }
        .title-block {
          display: flex;
          align-items: center;
          gap: 0px;
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
          gap: 4px;
          align-items: center;
          margin-left: auto;
        }
        .toggle-switch {
          position: relative;
          width: 40px;
          height: 22px;
          display: inline-block;
        }
        .toggle-switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }
        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: var(--toggle-off-color, #888);
          transition: 0.4s;
          border-radius: 11px;
          border: 1px solid var(--toggle-border-color, #666);
        }
        .slider:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 2px;
          bottom: 1.5px;
          background-color: var(--toggle-thumb-color, white);
          transition: 0.4s;
          border-radius: 50%;
          box-shadow: 0 1px 3px rgb(0 0 0 / 0.4);
        }
        input:checked + .slider {
          background-color: var(--toggle-on-color, #4caf50);
          border-color: var(--toggle-on-color, #4caf50);
        }
        input:checked + .slider:before {
          transform: translateX(18px);
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
        // .scroll-container {
        //   overflow-x: auto;
        // }
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
        }

        .date-wind-bar-segment {
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
        }

        .date-wind-bar {
          min-height: 4px;
          margin-top: 2px;
          display: flex;
          justify-content: center;
          align-items: flex-end;
          gap: 0px;
        }

      </style>

      <ha-card>
          <div class="title-block">
            <div class="icon-title-block">
              <ha-icon icon="mdi:windsock"></ha-icon>
            </div>
            <div class="text-title-block">
              <div class="card-title">${this.config.title || 'Kite Forecast'}</div>
              <div class="subtitle" id="subtitle"></div>
            </div>
            <div class="controls" id="controls-container">
              <span class="toggle-label">Night</span>
              <label class="toggle-switch" title="Toggle night hours">
                <input type="checkbox" id="toggle-night" ${this._showNight ? 'checked' : ''}>
                <span class="slider"></span>
              </label>
              <span class="toggle-label">Super Forecast</span>
              <label class="toggle-switch" title="Toggle forecast source (off=Forecast, on=Superforecast)">
                <input type="checkbox" id="toggle-source" ${this._defaultSource === 'superforecastdata' ? 'checked' : ''}>
                <span class="slider"></span>
              </label>
            </div>
          </div>
        <div class="scroll-container">
          <div id="dates-row" class="dates-row"></div>
          <div class="forecast-table" id="forecast-table"></div>
        </div>
        <div class="footer" id="footer"></div>
      </ha-card>
    `;

    this.querySelector("#toggle-night").onchange = () => {
      this._showNight = this.querySelector("#toggle-night").checked;
      this._applyNightVisibility();
    };

    this.querySelector("#toggle-source").onchange = () => {
      const checked = this.querySelector("#toggle-source").checked;
      this._selectedSource = checked ? 'superforecastdata' : 'forecastdata';
      //this.querySelector("#source-label").textContent = checked ? 'Superforecast' : 'Forecast';
      this._lastDataString = null;
      this._lastSource = null;
      this._updateFromSelectedSource();
    };

    // Initialize selected source
    //this._selectedSource = this._defaultSource;
  }

  set hass(hass) {
    this._hass = hass;
    this._updateFromSelectedSource();
  }

  _updateFromSelectedSource() {
    if (!this._hass) return;
    const entity = this.config.entity;
    const stateObj = this._hass.states[entity];
    if (!stateObj) return;

    //const sourceSelector = this.querySelector("#source-select");
    const controlsContainer = this.querySelector("#controls-container");
    const hasSuper = Array.isArray(stateObj.attributes.superforecastdata);
    const hasForecast = Array.isArray(stateObj.attributes.forecastdata);

    controlsContainer.style.display = hasSuper ? 'flex' : 'none';

    let source = this._selectedSource;
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

    //sourceSelector.value = source;
    this._selectedSource = source;

    const data = stateObj.attributes[source];
    if (!Array.isArray(data)) {
      this._clearDisplay("Forecast data is not an array");
      return;
    }

    const newDataString = JSON.stringify(data);
    if (this._lastDataString === newDataString && this._lastSource === source && this._lastActiveDay === this._activeDay) return;

    this._lastDataString = newDataString;
    this._lastSource = source;
    this._lastActiveDay = this._activeDay;

    const subtitle = this.querySelector("#subtitle");
    const footer = this.querySelector("#footer");
    const datesRow = this.querySelector("#dates-row");
    const forecastTable = this.querySelector("#forecast-table");
    const spot_name = stateObj.attributes.spot_name;
    const prefix = source === 'superforecastdata' ? 'superforecast' : 'forecast';
    const generated_at = stateObj.attributes[prefix + '_generated'];
    const fetched_at = stateObj.attributes[prefix + '_fetched'];

    // Parse generation date - use local timezone by default
    let generatedDate = new Date(generated_at);
    if (isNaN(generatedDate.getTime())) generatedDate = new Date();
    const now = new Date();
    const ageHours = (now - generatedDate) / 36e5;

    subtitle.textContent = `${spot_name || 'Unknown location'}`;

    // footer.textContent = `Updated ${generatedDate.toLocaleDateString('en-GB', {
    //   weekday: 'short', day: 'numeric', month: 'short'
    // })} ${generatedDate.toLocaleTimeString('en-GB', {
    //   hour: '2-digit', minute: '2-digit', hour12: false
    // })}`;

    const generatedStr = generatedDate.toLocaleDateString('en-GB', {
      weekday: 'short', day: 'numeric', month: 'short'
    }) + ' ' + generatedDate.toLocaleTimeString('en-GB', {
      hour: '2-digit', minute: '2-digit', hour12: false
    });

    const fetchedDate = new Date(fetched_at);
    const fetchedStr = isNaN(fetchedDate) ? '?' : fetchedDate.toLocaleTimeString('en-GB', {
      hour: '2-digit', minute: '2-digit', hour12: false
    });

    footer.textContent = `Generated ${generatedStr}, Fetched ${fetchedStr}`;


    footer.classList.toggle('warning', ageHours > 6);

    // Color map for wind speeds and temperature
    const wsColors = [
      "#9700ff", "#6400ff", "#3200ff", "#0032ff", "#0064ff", "#0096ff", "#00c7ff",
      "#00e6f0", "#25c192", "#11d411", "#00e600", "#00fa00", "#b8ff61", "#fffe00",
      "#ffe100", "#ffc800", "#ffaf00", "#ff9600", "#e67d00", "#e66400", "#dc4a1d",
      "#c8321d", "#b4191d", "#aa001d", "#b40032", "#c80064", "#fe0096"
    ];

    const getColorForWind = (speed) => {
      if (speed == null || isNaN(speed)) return 'inherit';
      const index = Math.min(wsColors.length - 1, Math.floor(speed / 2));
      return wsColors[index];
    };

    const getColorForTemperature = (temp) => {
      if (temp == null || isNaN(temp)) return 'inherit';
      const index = Math.floor((temp + 13) / 2); // since ws0 is for ≤ -13
      return wsColors[Math.max(0, Math.min(wsColors.length - 1, index))];
    };


    const groupedByDay = {};
    data.forEach(row => {
      const dt = new Date(row.datetime);
      if (isNaN(dt.getTime())) return;

      // Use en-CA for ISO-like yyyy-mm-dd grouping keys
      const dayKey = dt.toLocaleDateString('en-CA');

      if (!groupedByDay[dayKey]) groupedByDay[dayKey] = [];
      groupedByDay[dayKey].push(row);
    });

    if (!this._activeDay || !groupedByDay[this._activeDay]) {
      const todayKey = new Date().toLocaleDateString('en-CA');
      this._activeDay = groupedByDay[todayKey] ? todayKey : Object.keys(groupedByDay)[0];
    }

    datesRow.innerHTML = Object.keys(groupedByDay).map(day => {
      const activeClass = day === this._activeDay ? 'active' : '';

      // For display, you can still use 'nl-NL' or 'en-GB' or whatever you prefer
      const displayDay = new Date(day).toLocaleDateString('en-GB', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
      });

      // Wind bar for this day
      const windBars = groupedByDay[day].map(row => {
        const color = getColorForWind(row.wind_speed_kn);
        return `<div class="date-wind-bar-segment" style="background:${color};height:${row.wind_speed_kn}px;width:100%;display:inline-block;"></div>`;
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
        this._updateFromSelectedSource();
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

    // Render forecast body rows for active day (always render night rows)
    const body = forecastTable.querySelector(".forecast-body");
    const rowsHtml = groupedByDay[this._activeDay].map(row => {
      const nightClass = row.night_hour ? 'night' : '';

      // Rotate mdi:navigation icon by (deg + 180) % 360
      const rotateDir = deg => ((deg + 180) % 360);

      const windDirIcon = (row.wind_direction_deg != null)
        ? `<ha-icon icon="mdi:navigation" class="rotated" style="transform: rotate(${rotateDir(row.wind_direction_deg)}deg); --mdc-icon-size: 16px;"></ha-icon>`
        : '';

      const waveDirIcon = (row.wave_direction_deg != null)
        ? `<ha-icon icon="mdi:navigation" class="rotated" style="transform: rotate(${rotateDir(row.wave_direction_deg)}deg); --mdc-icon-size: 16px;" ></ha-icon>`
        : '';

      // Format time locally
      const dt = new Date(row.datetime);
      const timeStr = dt.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });

      // Format weather icon
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
          <div class="forecast-cell-value">${timeStr}</div>

          ${(() => {
            const bg = getColorForWind(row.wind_speed_kn);
            const fg = this._getContrastTextColor(bg);
            return `<div class="forecast-cell-value" style="background:${bg};color:${fg};">${row.wind_speed_kn?.toFixed(0) ?? '-'}</div>`;
          })()}

          ${(() => {
            const bg = getColorForWind(row.wind_gust_kn);
            const fg = this._getContrastTextColor(bg);
            return `<div class="forecast-cell-value" style="background:${bg};color:${fg};">${row.wind_gust_kn?.toFixed(0) ?? '-'}</div>`;
          })()}


          <div class="forecast-cell-value icon">${windDirIcon}</div>

          ${(() => {
            const bg = getColorForTemperature(row.temperature_c);
            const fg = this._getContrastTextColor(bg);
            return `<div class="forecast-cell-value icon" style="background:${bg};color:${fg};">${row.temperature_c?.toFixed(1) ?? '-'}</div>`;
          })()}

          <div class="forecast-cell-value icon">
              <ha-icon icon="${getWeatherIcon(row.cloud_cover_pct, row.rain_mm, row.night_hour)}" style="--mdc-icon-size: 16px;" title="${row.cloud_cover_pct?.toFixed(0) ?? '?'}% cloud, ${row.rain_mm?.toFixed(1) ?? '0'}mm rain"></ha-icon>
          </div>

          <div class="forecast-cell-value">${(row.rain_mm > 0 ? row.rain_mm.toFixed(1) : '-')}</div>

          <div class="forecast-cell-value">${row.air_pressure_hpa?.toFixed(0) ?? '-'}</div>
          <div class="forecast-cell-value icon">${waveDirIcon}</div>
          <div class="forecast-cell-value">${row.wave_height_m?.toFixed(1) ?? '-'}m<br>${row.wave_interval_s?.toFixed(0) ?? '-'} sec</div>
        </div>
      `;
    }).join('');
    body.innerHTML = rowsHtml;

    // Apply night visibility toggle
    this._applyNightVisibility();
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
    const rows = this.querySelectorAll('.forecast-row.night');
    rows.forEach(row => {
      row.style.display = this._showNight ? '' : 'none';
    });
  }

  _clearDisplay(msg) {
    const subtitle = this.querySelector("#subtitle");
    const footer = this.querySelector("#footer");
    const datesRow = this.querySelector("#dates-row");
    const forecastTable = this.querySelector("#forecast-table");

    subtitle.textContent = msg;
    footer.textContent = '';
    datesRow.innerHTML = '';
    forecastTable.innerHTML = '';
  }
}

if (!customElements.get('kite-forecast-card')) {
  customElements.define('kite-forecast-card', KiteForecastCard);
}
