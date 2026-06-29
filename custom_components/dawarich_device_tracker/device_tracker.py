"""Device tracker entities for Dawarich."""

from __future__ import annotations

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_TRACKER_ID, DOMAIN
from .coordinator import DawarichTrackerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Dawarich device trackers."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinators: dict[str, DawarichTrackerCoordinator] = runtime["coordinators"]
    trackers = runtime["trackers"]

    async_add_entities(
        DawarichDeviceTracker(entry, coordinators[tracker[CONF_TRACKER_ID]], tracker)
        for tracker in trackers
    )


class DawarichDeviceTracker(CoordinatorEntity[DawarichTrackerCoordinator], TrackerEntity):
    """Device tracker backed by the latest Dawarich point."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, coordinator: DawarichTrackerCoordinator, tracker: dict) -> None:
        super().__init__(coordinator)
        self._attr_name = tracker.get(CONF_NAME, coordinator.tracker_name)
        self._attr_unique_id = f"{entry.entry_id}_{coordinator.tracker_id}"

    @property
    def source_type(self) -> SourceType:
        """Return GPS source type so Home Assistant applies zone logic."""
        return SourceType.GPS

    @property
    def available(self) -> bool:
        """Return availability."""
        return super().available and self.coordinator.data is not None and not self.coordinator.is_stale

    @property
    def latitude(self) -> float | None:
        """Return latitude."""
        return self.coordinator.data.latitude if self.coordinator.data else None

    @property
    def longitude(self) -> float | None:
        """Return longitude."""
        return self.coordinator.data.longitude if self.coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict:
        """Return diagnostic attributes."""
        data = self.coordinator.data
        if data is None:
            return {"tracker_id": self.coordinator.tracker_id}
        return {
            "tracker_id": self.coordinator.tracker_id,
            "last_dawarich_timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "stale": self.coordinator.is_stale,
            "dawarich_point_id": data.raw.get("id"),
            "dawarich_tracker_id": data.raw.get("tracker_id"),
        }
