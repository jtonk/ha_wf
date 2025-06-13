class WindfinderCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error('Entity required');
    }
    this.config = config;
  }

  set hass(hass) {
    const entity = hass.states[this.config.entity];
    if (!entity) return;
    this.innerHTML = `
      <ha-card header="Windfinder">
        <div class="card-content">
          <div>Speed: ${entity.attributes.speed} m/s</div>
          <div>Direction: ${entity.attributes.direction}°</div>
          <div>Gust: ${entity.attributes.gust} m/s</div>
        </div>
      </ha-card>
    `;
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('windfinder-card', WindfinderCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'windfinder-card',
  name: 'Windfinder Card',
  preview: true,
  description: 'Shows wind conditions from Windfinder.'
});
