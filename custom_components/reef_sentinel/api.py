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
                params={"apiKey": self._api_key},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status in (401, 403):
                    raise ReefSentinelApiClientAuthError("Invalid API key")

                if response.status >= 400:
                    text = await response.text()
                    raise ReefSentinelApiClientError(
                        f"API request failed with status {response.status}: {text}"
                    )

                return await response.json()
        except asyncio.TimeoutError as err:
            raise ReefSentinelApiClientError("Request timed out") from err
        except aiohttp.ClientError as err:
            raise ReefSentinelApiClientError(f"Network error: {err}") from err
