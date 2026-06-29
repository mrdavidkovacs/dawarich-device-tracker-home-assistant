"""Dawarich API client."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

from aiohttp import ClientError, ClientResponseError, ClientSession


@dataclass(frozen=True)
class DawarichPoint:
    """Latest Dawarich point."""

    latitude: float
    longitude: float
    timestamp: datetime | None
    raw: dict[str, Any]


class DawarichApiError(Exception):
    """Raised when Dawarich cannot be queried."""


class DawarichClient:
    """Small client for the Dawarich points API."""

    def __init__(self, session: ClientSession, base_url: str, api_key: str, timeout: int) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    async def async_get_latest_point(self) -> DawarichPoint | None:
        """Return the newest non-anomalous point for this API key."""
        params = urlencode(
            {
                "api_key": self._api_key,
                "order": "desc",
                "per_page": 1,
            }
        )
        url = f"{self._base_url}/api/v1/points?{params}"

        try:
            async with asyncio.timeout(self._timeout):
                response = await self._session.get(url)
                response.raise_for_status()
                payload = await response.json()
        except (ClientResponseError, ClientError, TimeoutError) as err:
            raise DawarichApiError(str(err)) from err

        if not payload:
            return None

        if isinstance(payload, dict):
            points = payload.get("data") or payload.get("points") or []
            point = points[0] if points else payload
        else:
            point = payload[0]

        lat = _first_present(point, "latitude", "lat")
        lon = _first_present(point, "longitude", "lon", "lng")
        if lat is None or lon is None:
            raise DawarichApiError("latest point did not contain latitude/longitude")

        return DawarichPoint(
            latitude=float(lat),
            longitude=float(lon),
            timestamp=_parse_timestamp(_first_present(point, "timestamp", "time", "created_at")),
            raw=point,
        )


def _first_present(data: dict[str, Any], *keys: str) -> Any | None:
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def _parse_timestamp(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return datetime.fromtimestamp(int(text), tz=timezone.utc)
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None
