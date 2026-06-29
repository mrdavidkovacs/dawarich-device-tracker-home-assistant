# Dawarich Device Tracker

Custom Home Assistant integration that turns Dawarich accounts into GPS based `device_tracker` entities.

## What it does

- Adds one Dawarich instance through the Home Assistant UI.
- Adds one or more trackers below that instance, each with its own display name and Dawarich API key.
- Polls `GET /api/v1/points?order=desc&per_page=1` for each tracker.
- Exposes the newest latitude/longitude as a Home Assistant GPS device tracker.
- Marks a tracker unavailable when the newest Dawarich point is older than the configured stale timeout.

Because the entity is a GPS `device_tracker`, Home Assistant's normal zone handling applies automatically. Assign the tracker to a `person.*` entity and HA will resolve `home`, custom zones, or `not_home`.

## Setup

1. Copy `custom_components/dawarich_device_tracker` into the Home Assistant config directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration → Dawarich Device Tracker**.
4. Enter the Dawarich URL, polling interval, request timeout, stale timeout, and the first tracker API key.
5. Use **Configure** on the integration to add or remove more trackers.

## Notes

Dawarich's points endpoint currently omits accuracy and battery values, so this integration only exposes coordinates and diagnostic attributes. If Dawarich adds those fields later, the entity can pass them through without changing the basic zone logic.
