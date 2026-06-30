"""Dawarich Device Tracker integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import DawarichClient
from .const import (
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_STALE_AFTER,
    CONF_TIMEOUT,
    CONF_TRACKER_ID,
    CONF_TRACKERS,
    CONF_URL,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STALE_AFTER,
    DEFAULT_TIMEOUT,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import DawarichTrackerCoordinator

_LOGGER = logging.getLogger(__name__)


def _entry_value(entry: ConfigEntry, key: str, default):
    return entry.options.get(key, entry.data.get(key, default))


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dawarich Device Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    session = async_get_clientsession(hass, verify_ssl=_entry_value(entry, CONF_VERIFY_SSL, True))
    url = _entry_value(entry, CONF_URL, "")
    timeout = int(_entry_value(entry, CONF_TIMEOUT, DEFAULT_TIMEOUT))
    stale_after = int(_entry_value(entry, CONF_STALE_AFTER, DEFAULT_STALE_AFTER))
    scan_interval = int(_entry_value(entry, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    trackers = list(_entry_value(entry, CONF_TRACKERS, []))
    coordinators: dict[str, DawarichTrackerCoordinator] = {}

    _LOGGER.info(
        (
            "Setting up Dawarich Device Tracker entry %s with %d tracker(s); "
            "scan_interval=%ss, timeout=%ss, stale_after=%ss"
        ),
        entry.entry_id,
        len(trackers),
        scan_interval,
        timeout,
        stale_after,
    )

    for tracker in trackers:
        tracker_id = tracker[CONF_TRACKER_ID]
        api_key = tracker[CONF_API_KEY]
        client = DawarichClient(session, url, api_key, timeout)
        coordinator = DawarichTrackerCoordinator(
            hass,
            client,
            name=tracker.get(CONF_NAME, tracker_id),
            tracker_id=tracker_id,
            scan_interval=scan_interval,
            stale_after=stale_after,
        )
        coordinators[tracker_id] = coordinator

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinators": coordinators,
        "trackers": trackers,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    for coordinator in coordinators.values():
        entry.async_create_background_task(
            hass,
            coordinator.async_request_refresh(),
            f"{DOMAIN}_{coordinator.tracker_id}_initial_refresh",
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
