"""Serve and register the bundled Windfinder dashboard card."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, lovelace
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

CARD_PATH = "/windfinder/ha_wf_card.js"
CARD_FILE = Path(__file__).parent / "frontend" / "ha_wf_card.js"


async def async_register_card(hass: HomeAssistant) -> None:
    """Make the card available in storage and YAML resource modes."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_PATH, str(CARD_FILE), False)]
    )

    integration = await async_get_integration(hass, DOMAIN)
    card_url = f"{CARD_PATH}?v={integration.version}"
    resources = hass.data[lovelace.DOMAIN].resources
    await resources.async_get_info()

    if isinstance(resources, lovelace.resources.ResourceStorageCollection):
        for resource in resources.async_items():
            if resource["url"].split("?", 1)[0] != CARD_PATH:
                continue
            if resource["url"] != card_url or resource["res_type"] != "module":
                await resources.async_update_item(
                    resource["id"], {"res_type": "module", "url": card_url}
                )
            return
        await resources.async_create_item({"res_type": "module", "url": card_url})
    elif not any(
        resource["url"].split("?", 1)[0] == CARD_PATH
        for resource in resources.async_items()
    ):
        # YAML resources are read-only; this loads the same bundled module.
        frontend.add_extra_js_url(hass, card_url)
