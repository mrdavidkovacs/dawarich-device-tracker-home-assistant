"""Dawarich update coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import DawarichApiError, DawarichClient, DawarichPoint

_LOGGER = logging.getLogger(__name__)


class DawarichTrackerCoordinator(DataUpdateCoordinator[DawarichPoint | None]):
    """Fetch one Dawarich account's latest point."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DawarichClient,
        *,
        name: str,
        tracker_id: str,
        scan_interval: int,
        stale_after: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"Dawarich {name}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.tracker_name = name
        self.tracker_id = tracker_id
        self.stale_after = stale_after

    async def _async_update_data(self) -> DawarichPoint | None:
        try:
            return await self.client.async_get_latest_point()
        except DawarichApiError as err:
            raise UpdateFailed(str(err)) from err

    @property
    def is_stale(self) -> bool:
        """Return true if the newest point is older than the configured stale timeout."""
        if self.data is None or self.data.timestamp is None:
            return False
        age = dt_util.utcnow() - self.data.timestamp
        return age.total_seconds() > self.stale_after
