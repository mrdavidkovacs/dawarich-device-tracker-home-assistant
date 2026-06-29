"""Config flow for Dawarich Device Tracker."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

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
)


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "dawarich_tracker"


def _base_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_URL, default=defaults.get(CONF_URL, "https://")): str,
            vol.Required(CONF_VERIFY_SSL, default=defaults.get(CONF_VERIFY_SSL, True)): BooleanSelector(),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): NumberSelector(
                NumberSelectorConfig(min=30, max=3600, step=10, mode=NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_TIMEOUT, default=defaults.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)): NumberSelector(
                NumberSelectorConfig(min=5, max=120, step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_STALE_AFTER,
                default=defaults.get(CONF_STALE_AFTER, DEFAULT_STALE_AFTER),
            ): NumberSelector(
                NumberSelectorConfig(min=60, max=86400, step=60, mode=NumberSelectorMode.BOX)
            ),
        }
    )


def _tracker_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Optional(CONF_TRACKER_ID, default=defaults.get(CONF_TRACKER_ID, "")): str,
            vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, "")): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
        }
    )


class DawarichDeviceTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Dawarich Device Tracker config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Configure the Dawarich instance."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_tracker()

        return self.async_show_form(step_id="user", data_schema=_base_schema())

    async def async_step_tracker(self, user_input: dict[str, Any] | None = None):
        """Add the first tracker for the instance."""
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            tracker_id = user_input.get(CONF_TRACKER_ID) or _slugify(name)
            if not user_input[CONF_API_KEY].strip():
                errors[CONF_API_KEY] = "required"
            else:
                self._data[CONF_TRACKERS] = [
                    {
                        CONF_NAME: name,
                        CONF_TRACKER_ID: _slugify(tracker_id),
                        CONF_API_KEY: user_input[CONF_API_KEY].strip(),
                    }
                ]
                await self.async_set_unique_id(self._data[CONF_URL].rstrip("/"))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Dawarich ({self._data[CONF_URL]})", data=self._data)

        return self.async_show_form(step_id="tracker", data_schema=_tracker_schema(), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow."""
        return DawarichOptionsFlow(config_entry)


class DawarichOptionsFlow(config_entries.OptionsFlow):
    """Manage Dawarich trackers and polling settings."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry
        self._options = {**entry.data, **entry.options}

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Show menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["settings", "add_tracker", "remove_tracker"],
        )

    async def async_step_settings(self, user_input: dict[str, Any] | None = None):
        """Update instance settings."""
        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(title="", data=self._options)
        return self.async_show_form(step_id="settings", data_schema=_base_schema(self._options))

    async def async_step_add_tracker(self, user_input: dict[str, Any] | None = None):
        """Add a tracker to this Dawarich instance."""
        errors: dict[str, str] = {}
        trackers = list(self._options.get(CONF_TRACKERS, []))
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            tracker_id = _slugify(user_input.get(CONF_TRACKER_ID) or name)
            if any(tracker[CONF_TRACKER_ID] == tracker_id for tracker in trackers):
                errors[CONF_TRACKER_ID] = "already_exists"
            elif not user_input[CONF_API_KEY].strip():
                errors[CONF_API_KEY] = "required"
            else:
                trackers.append(
                    {
                        CONF_NAME: name,
                        CONF_TRACKER_ID: tracker_id,
                        CONF_API_KEY: user_input[CONF_API_KEY].strip(),
                    }
                )
                self._options[CONF_TRACKERS] = trackers
                return self.async_create_entry(title="", data=self._options)
        return self.async_show_form(step_id="add_tracker", data_schema=_tracker_schema(), errors=errors)

    async def async_step_remove_tracker(self, user_input: dict[str, Any] | None = None):
        """Remove a tracker from this Dawarich instance."""
        trackers = list(self._options.get(CONF_TRACKERS, []))
        choices = [tracker[CONF_TRACKER_ID] for tracker in trackers]
        if user_input is not None:
            remove_id = user_input[CONF_TRACKER_ID]
            self._options[CONF_TRACKERS] = [
                tracker for tracker in trackers if tracker[CONF_TRACKER_ID] != remove_id
            ]
            return self.async_create_entry(title="", data=self._options)

        if not choices:
            return self.async_abort(reason="no_trackers")

        return self.async_show_form(
            step_id="remove_tracker",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TRACKER_ID): SelectSelector(
                        SelectSelectorConfig(options=choices, mode=SelectSelectorMode.DROPDOWN)
                    )
                }
            ),
        )
