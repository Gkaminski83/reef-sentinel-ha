"""Sensor platform for Reef Sentinel."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import ReefSentinelDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class ReefSentinelSensorDescription(SensorEntityDescription):
    """Describes Reef Sentinel sensor entity."""

    data_group: str | None = None
    data_key: str


SENSORS: tuple[ReefSentinelSensorDescription, ...] = (
    ReefSentinelSensorDescription(
        key="reef_health_score",
        name="reef_health_score",
        data_key="healthScore",
    ),
    ReefSentinelSensorDescription(
        key="reef_risk_level",
        name="reef_risk_level",
        data_key="riskLevel",
    ),
    ReefSentinelSensorDescription(
        key="reef_kh",
        name="reef_kh",
        data_group="parameters",
        data_key="kh",
        native_unit_of_measurement="dKH",
    ),
    ReefSentinelSensorDescription(
        key="reef_no3",
        name="reef_no3",
        data_group="parameters",
        data_key="no3",
        native_unit_of_measurement="mg/L",
    ),
    ReefSentinelSensorDescription(
        key="reef_po4",
        name="reef_po4",
        data_group="parameters",
        data_key="po4",
        native_unit_of_measurement="mg/L",
    ),
    ReefSentinelSensorDescription(
        key="reef_ph",
        name="reef_ph",
        data_group="parameters",
        data_key="ph",
    ),
    ReefSentinelSensorDescription(
        key="reef_temperature",
        name="reef_temperature",
        data_group="parameters",
        data_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    ReefSentinelSensorDescription(
        key="reef_salinity",
        name="reef_salinity",
        data_group="parameters",
        data_key="salinity",
        native_unit_of_measurement="ppt",
    ),
    ReefSentinelSensorDescription(
        key="reef_kh_trend",
        name="reef_kh_trend",
        data_group="trends",
        data_key="kh",
    ),
    ReefSentinelSensorDescription(
        key="reef_no3_trend",
        name="reef_no3_trend",
        data_group="trends",
        data_key="no3",
    ),
    ReefSentinelSensorDescription(
        key="reef_po4_trend",
        name="reef_po4_trend",
        data_group="trends",
        data_key="po4",
    ),
    ReefSentinelSensorDescription(
        key="reef_last_update",
        name="reef_last_update",
        data_key="updatedAt",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Reef Sentinel sensors from config entry."""
    coordinator: ReefSentinelDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        ReefSentinelSensor(coordinator, entry, description)
        for description in SENSORS
    )


class ReefSentinelSensor(
    CoordinatorEntity[ReefSentinelDataUpdateCoordinator], SensorEntity
):
    """Reef Sentinel sensor."""

    entity_description: ReefSentinelSensorDescription

    def __init__(
        self,
        coordinator: ReefSentinelDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ReefSentinelSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for all entities."""
        return DeviceInfo(
            identifiers={(DOMAIN, "reef_tank")},
            name="Reef Tank",
            manufacturer="Reef Sentinel",
            model="Cloud Tank",
        )

    @property
    def native_value(self) -> Any:
        """Return sensor state from coordinator data."""
        data = self.coordinator.data
        if not data:
            return None

        desc = self.entity_description
        payload: Any = data
        if desc.data_group:
            payload = data.get(desc.data_group, {})

        value = payload.get(desc.data_key) if isinstance(payload, dict) else None

        if desc.key == "reef_last_update" and isinstance(value, str):
            parsed: datetime | None = dt_util.parse_datetime(value)
            return parsed

        return value
