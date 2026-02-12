"""Config flow for Reef Sentinel integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    ReefSentinelApiClient,
    ReefSentinelApiClientAuthError,
    ReefSentinelApiClientConnectionError,
    ReefSentinelApiClientInvalidResponseError,
    ReefSentinelApiClientServerError,
    ReefSentinelApiClientTimeoutError,
)
from .const import CONF_API_KEY, DOMAIN


class ReefSentinelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Reef Sentinel."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            try:
                await self._validate_api_key(api_key)
            except ReefSentinelApiClientAuthError:
                errors["base"] = "invalid_auth"
            except ReefSentinelApiClientTimeoutError:
                errors["base"] = "timeout"
            except ReefSentinelApiClientServerError:
                errors["base"] = "server_error"
            except ReefSentinelApiClientInvalidResponseError:
                errors["base"] = "invalid_response"
            except ReefSentinelApiClientConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pragma: no cover
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id("reef_sentinel_account")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Reef Sentinel",
                    data={CONF_API_KEY: api_key},
                )

        schema = vol.Schema({vol.Required(CONF_API_KEY): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _validate_api_key(self, api_key: str) -> None:
        """Validate user-provided API key with Reef Sentinel API."""
        session = async_get_clientsession(self.hass)
        client = ReefSentinelApiClient(api_key=api_key, session=session)
        await client.get_status()
