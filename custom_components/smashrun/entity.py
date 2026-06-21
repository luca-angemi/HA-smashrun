"""Entity representing a Smashrun device."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN


class SmashrunEntity(CoordinatorEntity):
    """Representation of a Smashrun entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        description: EntityDescription,
        coordinator,
    ) -> None:
        """Initialize a Smashrun entity."""
        super().__init__(coordinator)
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, "Luca")},
            entry_type=dr.DeviceEntryType.SERVICE,
        )
        self.entity_description = description
        self._attr_unique_id = slugify(DOMAIN + " " + description.key, separator="_")
