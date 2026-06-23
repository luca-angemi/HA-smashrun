"""Number platform for Smashrun."""
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity

from .entity import SmashrunEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = config_entry.runtime_data

    async_add_entities(
        [
            SmashrunRunCountOffset(
                config_entry,
                NumberEntityDescription(
                    key="run_count_offset",
                    name="Run Count Offset",
                    translation_key="run_count_offset"
                ),
                coordinator,
            )
        ]
    )


class SmashrunRunCountOffset(SmashrunEntity, RestoreEntity, NumberEntity):
    """Offset to subtract from run_count."""

    _attr_native_min_value = 0
    _attr_native_max_value = 10000
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_native_value = 0

    async def async_added_to_hass(self) -> None:
        """Restore last value on restart."""
        await RestoreEntity.async_added_to_hass(self)
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._attr_native_value = int(float(last_state.state))
            except (ValueError, TypeError):
                pass

        self.coordinator.run_count_offset = self._attr_native_value
        self.async_write_ha_state()



    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        self._attr_native_value = int(value)
        self.coordinator.run_count_offset = value
        self.async_write_ha_state()
        self.coordinator.async_update_listeners()