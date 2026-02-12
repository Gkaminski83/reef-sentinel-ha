"""Data coordinator for Reef Sentinel."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ReefSentinelApiClient, ReefSentinelApiClientError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ReefSentinelDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Reef Sentinel data."""

    def __init__(self, hass: HomeAssistant, api: ReefSentinelApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest data from API."""
        try:
            return await self.api.get_status()
        except ReefSentinelApiClientError as err:
            raise UpdateFailed("API request failed") from err
