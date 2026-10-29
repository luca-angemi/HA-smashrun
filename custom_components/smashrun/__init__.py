"""The Smashrun integration."""

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import SmashrunCoordinator
from .service import async_setup_services

PLATFORMS: list[Platform] = [Platform.IMAGE, Platform.NUMBER, Platform.SENSOR]

type SmashrunConfigEntry = ConfigEntry[SmashrunCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: SmashrunConfigEntry
) -> None:
    """Set up Smashrun from a config entry."""

    coordinator = SmashrunCoordinator(hass, config_entry)
    await coordinator.async_refresh()
    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    async_setup_services(hass, config_entry)


async def async_unload_entry(
    hass: HomeAssistant, config_entry: SmashrunConfigEntry
) -> None:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
