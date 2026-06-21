"""Coordinator for Smashrun."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import create_async_httpx_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import (
    add_trailings,
    enrich_with_stats,
    enrich_with_vo2,
    fetch_image_data,
    fetch_latest_run,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmashrunCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching and updating Smashrun data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the Smashrun coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(hours=6),
            always_update=False,
        )
        self.client = create_async_httpx_client(hass, timeout=30)
        self.smashrun_token = config_entry.data.get(CONF_TOKEN)

    async def _async_update_data(self):
        """Fetch and process data from Smashrun API."""
        token = self.smashrun_token
        client = self.client
        run = await fetch_latest_run(client, token)
        await enrich_with_stats(client, token, run)
        await enrich_with_vo2(run)
        await add_trailings(client, token, run)
        await fetch_image_data(run)
        if self.data and run["map_image"] == self.data["map_image"]:
            run["map_image_last_updated"] = self.data["map_image_last_updated"]
        return run
