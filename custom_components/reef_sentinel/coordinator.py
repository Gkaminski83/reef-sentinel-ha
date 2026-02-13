"""Data coordinator for Reef Sentinel."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ReefSentinelApiClient, ReefSentinelApiClientError
from .const import CONF_API_KEY, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)
WEBHOOK_URL = "https://app.reef-sentinel.pl/api/integrations/home-assistant/webhook"


class ReefSentinelDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Reef Sentinel data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: ReefSentinelApiClient,
        entry: ConfigEntry,
        session: aiohttp.ClientSession,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self._entry = entry
        self._session = session
        self._api_key: str = entry.data[CONF_API_KEY]

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest data from API."""
        try:
            data = await self.api.get_status()
        except ReefSentinelApiClientError as err:
            raise UpdateFailed("API request failed") from err

        await self.push_sensor_data()
        return data

    async def push_sensor_data(self) -> None:
        """Push selected Home Assistant sensor data to Reef Sentinel webhook."""
        payload = self._build_sensor_payload()
        if payload is None:
            return

        try:
            async with self._session.post(
                WEBHOOK_URL,
                headers={
                    "X-API-Key": self._api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status >= 400:
                    _LOGGER.warning(
                        "Failed to push sensor data to Reef Sentinel webhook"
                    )
        except (aiohttp.ClientError, TimeoutError):
            _LOGGER.warning("Failed to push sensor data to Reef Sentinel webhook")

    def _build_sensor_payload(self) -> dict[str, Any] | None:
        """Build webhook payload from available Home Assistant sensor states."""
        sensor_values: dict[str, float] = {}

        mapping = {
            "temperature": self._resolve_entity_candidates(
                option_key="temperature_entity_id",
                fallback_candidates=[
                    "sensor.temperature",
                    "sensor.water_temperature",
                    "sensor.reef_temperature",
                ],
            ),
            "ph": self._resolve_entity_candidates(
                option_key="ph_entity_id",
                fallback_candidates=["sensor.ph", "sensor.reef_ph"],
            ),
            "salinity": self._resolve_entity_candidates(
                option_key="salinity_entity_id",
                fallback_candidates=["sensor.salinity", "sensor.reef_salinity"],
            ),
            "orp": self._resolve_entity_candidates(
                option_key="orp_entity_id",
                fallback_candidates=["sensor.orp", "sensor.reef_orp"],
            ),
        }

        for payload_key, entity_ids in mapping.items():
            value = self._first_numeric_state(entity_ids)
            if value is not None:
                sensor_values[payload_key] = value

        if not sensor_values:
            return None

        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "sensors": sensor_values,
        }

    def _resolve_entity_candidates(
        self, option_key: str, fallback_candidates: list[str]
    ) -> list[str]:
        """Resolve configured entity candidates from options/data with fallback."""
        configured = self._entry.options.get(option_key) or self._entry.data.get(option_key)
        if isinstance(configured, str) and configured.strip():
            return [configured.strip()]
        return fallback_candidates

    def _first_numeric_state(self, entity_ids: list[str]) -> float | None:
        """Return first numeric sensor state from candidate entity IDs."""
        for entity_id in entity_ids:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in ("unknown", "unavailable", ""):
                continue
            try:
                return float(state.state)
            except (TypeError, ValueError):
                continue
        return None
