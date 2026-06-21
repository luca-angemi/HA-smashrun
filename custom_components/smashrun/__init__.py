"""The Smashrun integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import SmashrunCoordinator
from .service import async_setup_services

PLATFORMS: list[Platform] = [Platform.IMAGE, Platform.SENSOR]

type SmashrunConfigEntry = ConfigEntry[SmashrunCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: SmashrunConfigEntry
) -> bool:
    """Set up Smashrun from a config entry."""

    coordinator = SmashrunCoordinator(hass, config_entry)
    await coordinator.async_refresh()
    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    async_setup_services(hass, config_entry)

    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: SmashrunConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
