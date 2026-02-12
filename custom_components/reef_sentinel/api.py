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


class ReefSentinelApiClientConnectionError(ReefSentinelApiClientError):
    """API client connection error."""


class ReefSentinelApiClientTimeoutError(ReefSentinelApiClientError):
    """API client timeout error."""


class ReefSentinelApiClientServerError(ReefSentinelApiClientError):
    """API client server-side error."""


class ReefSentinelApiClientInvalidResponseError(ReefSentinelApiClientError):
    """API client invalid response error."""


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
                if response.status in (401, 403):
                    raise ReefSentinelApiClientAuthError("Invalid API key")
                if response.status >= 500:
                    raise ReefSentinelApiClientServerError("API server error")
                if response.status >= 400:
                    raise ReefSentinelApiClientConnectionError("API request failed")

                try:
                    payload = await response.json()
                except (aiohttp.ContentTypeError, ValueError) as err:
                    raise ReefSentinelApiClientInvalidResponseError(
                        "Invalid API response"
                    ) from err

                if not isinstance(payload, dict):
                    raise ReefSentinelApiClientInvalidResponseError(
                        "Invalid API response"
                    )

                return payload
        except asyncio.TimeoutError as err:
            raise ReefSentinelApiClientTimeoutError("API request timed out") from err
        except aiohttp.ClientError as err:
            raise ReefSentinelApiClientConnectionError("API request failed") from err
