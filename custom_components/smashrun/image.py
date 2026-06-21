"""Images of the Smashrun component."""

import logging

from homeassistant.components.image import ImageEntity, ImageEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import SmashrunEntity

_LOGGER = logging.getLogger(__name__)

IMAGE_TYPE = ImageEntityDescription(key="smashrun_polyline_route", name="Route")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up image entities."""
    async_add_entities([SmashrunImage(hass, IMAGE_TYPE, config_entry)])


class SmashrunImage(SmashrunEntity, ImageEntity):
    """Representation of a Smashrun image entity."""

    _attr_content_type = "image/png"

    def __init__(self, hass: HomeAssistant, description, config_entry) -> None:
        """Initialize the image entity."""
        SmashrunEntity.__init__(self, hass, description, config_entry.runtime_data)
        ImageEntity.__init__(self, hass)

    async def async_image(self) -> bytes | None:
        """Return bytes of the image from coordinator data."""
        return self.coordinator.data.get("map_image")

    @property
    def image_last_updated(self):
        """Return the last updated timestamp of the image."""
        return self.coordinator.data.get("map_image_last_updated")
