"""Reef Sentinel API client."""

from __future__ import annotations

from typing import Any

import asyncio
import aiohttp

from .const import API_BASE


class ReefSentinelApiClientError(Exception):
    """Base API client error."""


class ReefSentinelApiClientAuthError(ReefSentinelApiClientError):
    """API client authentication error."""


class ReefSentinelApiClient:
    """Simple client for the Reef Sentinel API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        self._api_key = api_key
        self._session = session

    async def get_status(self) -> dict[str, Any]:
        """Fetch tank status from Reef Sentinel."""
        try:
            async with self._session.get(
                API_BASE,
                headers={"X-API-Key": self._api_key},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status != 200:
                    raise ReefSentinelApiClientAuthError("Invalid API key")

                return await response.json()
        except asyncio.TimeoutError as err:
            raise ReefSentinelApiClientError("API request failed") from err
        except aiohttp.ClientError as err:
            raise ReefSentinelApiClientError("API request failed") from err
