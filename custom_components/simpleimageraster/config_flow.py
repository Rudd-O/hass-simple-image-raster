"""Config flow for the IPP printing integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult

from .const import DOMAIN
from .const import DOMAIN as INTEGRATION_NAME

_LOGGER = logging.getLogger(__name__)


class SimpleImageRasterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IPP printing."""

    VERSION = 1

    async def async_get_integration_entry(self) -> ConfigEntry | None:
        """Return the main integration config entry, if it exists."""
        existing_entries = self.hass.config_entries.async_entries(
            domain=DOMAIN, include_ignore=False, include_disabled=False
        )
        for entry in existing_entries:
            if entry.title == INTEGRATION_NAME:
                return entry
        return None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")
    
        return self.async_create_entry(
            title="Simple image raster",
            data={},
        )    
