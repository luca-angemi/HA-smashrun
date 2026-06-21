"""Sensors of the Smashrun component."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfLength, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .entity import SmashrunEntity

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPE_SMASHRUN: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="activityId",
        translation_key="activity_id",
        name="Activity Id",
    ),
    SensorEntityDescription(
        key="distance",
        name="Distance",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="duration",
        name="Duration",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="calories",
        name="Calories",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_CALORIE,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="startDateTimeLocal",
        name="Start Date Time",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="totalDistance",
        name="Total Distance",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="cmDistance",
        name="Current Month Distance",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="cyDistance",
        name="Current Year Distance",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="vo2_max",
        translation_key="vo2_max",
        name="VO2 max",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="ml/min/kg",
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="trailing_7_days",
        name="Trailing 7 days",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="trailing_30_days",
        name="Trailing 30 days",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="trailing_90_days",
        name="Trailing 90 days",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="trailing_365_days",
        name="Trailing 365 days",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="run_count",
        translation_key="run_count",
        name="Run Count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="powerAverage",
        name="Average Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Smashrun sensor."""
    coordinator = config_entry.runtime_data
    entities = [
        SmashrunSensor(config_entry, stype, coordinator)
        for stype in SENSOR_TYPE_SMASHRUN
    ]

    async_add_entities(entities)


class SmashrunSensor(SmashrunEntity, SensorEntity):
    """Smashrun Sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        data = self.coordinator.data
        try:
            return data[self.entity_description.key]
        except (KeyError, TypeError, IndexError):
            return None
