# Dawarich Device Tracker for Home Assistant

A Home Assistant custom integration that turns one or more [Dawarich](https://dawarich.app/) accounts into GPS based `device_tracker` entities.

It is useful when you want Dawarich as the location-history app, but do **not** want to install the Home Assistant Companion App on a phone just to get presence tracking.

## Features

- Configure a Dawarich instance from the Home Assistant UI.
- Add multiple trackers to one Dawarich instance.
- Each tracker has its own name, optional tracker ID, and Dawarich API key.
- Configurable polling interval.
- Configurable HTTP request timeout.
- Configurable stale timeout for old location points.
- Exposes GPS `device_tracker` entities with latitude and longitude.
- Works with Home Assistant zones and `person.*` entities.
- No YAML configuration required.

## How it works

For each configured tracker, the integration polls the newest Dawarich point:

```text
GET /api/v1/points?order=desc&per_page=1
```

The returned latitude and longitude are exposed as a Home Assistant GPS tracker. Because the tracker uses Home Assistant's GPS device-tracker model, Home Assistant performs the usual zone matching:

- inside `zone.home` → `home`
- inside another zone → that zone name
- outside all zones → `not_home`

Assign the generated `device_tracker.*` entity to a `person.*` entity if you want normal person-presence behaviour.

## Installation with HACS

This integration is intended to be installed as a HACS custom repository.

1. Open Home Assistant.
2. Go to **HACS → Integrations**.
3. Open the three-dot menu in the top right.
4. Choose **Custom repositories**.
5. Add this repository URL:

   ```text
   https://github.com/mrdavidkovacs/dawarich-device-tracker-home-assistant
   ```

6. Set the category to **Integration**.
7. Click **Add**.
8. Search for **Dawarich Device Tracker** in HACS.
9. Install it.
10. Restart Home Assistant.

## Manual installation

If you do not use HACS:

1. Copy this directory into your Home Assistant config directory:

   ```text
   custom_components/dawarich_device_tracker
   ```

2. Restart Home Assistant.

The final path should look like this:

```text
/config/custom_components/dawarich_device_tracker/manifest.json
```

## Configuration

After installation and restart:

1. Go to **Settings → Devices & services**.
2. Click **Add integration**.
3. Search for **Dawarich Device Tracker**.
4. Enter the Dawarich instance settings.
5. Add the first tracker.

### Dawarich instance settings

- **Dawarich URL**  
  The base URL of your Dawarich instance, for example:

  ```text
  https://dawarich.example.com
  ```

- **Verify SSL certificate**  
  Keep enabled for a normal HTTPS setup. Disable only for local/self-signed setups where you understand the risk.

- **Polling interval in seconds**  
  How often Home Assistant polls Dawarich. A practical value is usually `120` to `300` seconds.

- **Request timeout in seconds**  
  How long Home Assistant waits for Dawarich before considering a poll failed.

- **Stale timeout in seconds**  
  If the newest Dawarich point is older than this, the tracker is marked unavailable. This prevents a phone that stopped reporting hours ago from looking deceptively current. A practical value is `3600` seconds.

### Tracker settings

Each tracker represents one Dawarich API key/account.

- **Tracker name**  
  Friendly display name in Home Assistant.

- **Tracker ID**  
  Optional stable identifier used for the entity's unique ID basis. If omitted, the name is converted into a slug.

- **Dawarich API key**  
  API key for the Dawarich account to poll. It is entered through a password field in the Home Assistant UI.

## Adding more trackers

After the integration is configured:

1. Go to **Settings → Devices & services**.
2. Open **Dawarich Device Tracker**.
3. Click **Configure**.
4. Choose **Add device tracker**.
5. Enter the name, optional tracker ID, and API key.

You can also use the same **Configure** menu to update instance settings or remove trackers.

## Using with persons and zones

After a tracker is created, Home Assistant will expose a `device_tracker.*` entity.

To use it as a person tracker:

1. Go to **Settings → People**.
2. Open or create the person.
3. Add the generated Dawarich `device_tracker.*` entity as a tracking device.

Home Assistant will then apply your existing zones automatically.

## Recommended settings

For normal family presence tracking:

- Polling interval: `120` or `300` seconds
- Request timeout: `15` seconds
- Stale timeout: `3600` seconds

For faster presence changes, lower the polling interval. Be kind to your Dawarich instance; it has other things to do than answer the same question every ten seconds.

## Privacy and security notes

- People tracked by this integration do **not** need access to your Home Assistant instance.
- They only need to run a Dawarich-compatible tracking app that writes to Dawarich.
- Home Assistant reads the newest point from Dawarich via API key.
- Protect Dawarich API keys like passwords.
- Prefer a separate Dawarich account/API key per person.

## Current limitations

- The integration currently exposes coordinates and diagnostic attributes.
- Battery level and GPS accuracy are not exposed because the standard Dawarich points response does not reliably include them.
- The integration polls Dawarich; it does not receive push updates.

## Troubleshooting

### The integration is not visible after installation

Restart Home Assistant after installing the integration. Custom integrations are discovered at startup.

### The tracker is unavailable

Check:

- Dawarich URL is reachable from Home Assistant.
- The API key is correct.
- The newest Dawarich point is newer than the configured stale timeout.
- SSL verification matches your Dawarich certificate setup.

### The person is not entering zones

Check:

- The generated `device_tracker.*` entity has latitude and longitude attributes.
- The tracker is assigned to the correct `person.*` entity.
- Your Home Assistant zones have the expected radius and location.

### The tracker updates too slowly

Lower the polling interval in the integration options. For most setups, avoid going below 60 seconds unless you have a specific reason.

## Development

The integration lives under:

```text
custom_components/dawarich_device_tracker
```

Basic local checks:

```bash
python -m compileall -q -b custom_components/dawarich_device_tracker
python -m json.tool custom_components/dawarich_device_tracker/manifest.json
python -m json.tool custom_components/dawarich_device_tracker/strings.json
```

## License

MIT
