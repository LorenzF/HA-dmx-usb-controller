"""Adds config flow for Blueprint."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ID, CONF_NAME
from homeassistant.helpers import selector
from slugify import slugify

from .const import DOMAIN


class USBDMXConfigHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                unique_id=slugify(
                    f"dmx_{user_input[CONF_NAME]}_{int(user_input[CONF_ID]):03d}"
                )
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Required(CONF_ID): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=512,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                },
            ),
            errors=_errors,
        )
