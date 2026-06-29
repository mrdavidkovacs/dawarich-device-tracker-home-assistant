"""Constants for the Dawarich Device Tracker integration."""

DOMAIN = "dawarich_device_tracker"

CONF_URL = "url"
CONF_VERIFY_SSL = "verify_ssl"
CONF_TRACKERS = "trackers"
CONF_TRACKER_ID = "tracker_id"
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_TIMEOUT = "timeout"
CONF_STALE_AFTER = "stale_after"

DEFAULT_SCAN_INTERVAL = 120
DEFAULT_TIMEOUT = 15
DEFAULT_STALE_AFTER = 3600

PLATFORMS = ["device_tracker"]
