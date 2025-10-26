"""Light platform for usb_dmx."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.components.light.const import ColorMode
from homeassistant.const import CONF_ID, CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo
from PyDMXControl.controllers import uDMXController
from PyDMXControl.profiles.Generic import Dimmer

from .const import DOMAIN

if TYPE_CHECKING:
    from typing import Any

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import UndefinedType


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    if hass.data[DOMAIN].get("dmx_controller") is None:
        hass.data[DOMAIN]["dmx_controller"] = uDMXController()

    async_add_entities(
        [
            DMXLightEntity(
                dmx_id=entry.data[CONF_ID],
                controller=hass.data[DOMAIN]["dmx_controller"],
                entity_description=LightEntityDescription(
                    key="DMX Lights",
                    name=entry.data[CONF_NAME],
                    icon="mdi:lightbulb-on-50",
                ),
            )
        ]
    )


class DMXLightEntity(LightEntity):
    """DMX light class."""

    SMOOTH_MS = 500

    def __init__(
        self,
        controller: uDMXController,
        dmx_id: int,
        entity_description: LightEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        self.dmx_id = int(dmx_id)
        self.entity_description = entity_description

        self._fixture = controller.add_fixture(
            fixture=Dimmer, name=self.entity_description.name, start_channel=self.dmx_id
        ).dim(0)

        self._brightness = 0
        self._state = False

        self._attr_unique_id = f"dmx_{self.dmx_id:03d}"
        self._attr_device_info = DeviceInfo(
            name=str(self.entity_description.name),
            identifiers={
                (
                    str(self.entity_description.name),
                    str(self.dmx_id),
                ),
            },
        )

    @property
    def name(self) -> str | UndefinedType | None:
        """Name of the entity."""
        return self.entity_description.name

    @property
    def unique_id(self) -> str | None:
        """unique_id of the entity."""
        return f"dmx_{self.dmx_id:03d}"

    @property
    def color_mode(self) -> ColorMode:
        """Return colormode brightness."""
        return ColorMode.BRIGHTNESS

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        """Flag supported features."""
        return {ColorMode.BRIGHTNESS}

    @property
    def brightness(self) -> int:
        """Brightness of dmx light."""
        return self._brightness

    @property
    def is_on(self) -> bool:
        """Check if dmx light is on."""
        return self._state

    def turn_on(self, **kwargs: dict[str, Any]) -> None:
        """Turn on dmx light."""
        self._state = True

        new_brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        if isinstance(new_brightness, int):
            self._brightness = new_brightness
        self._fixture.dim(self._brightness, self.SMOOTH_MS)

    def turn_off(self) -> None:
        """Turn off dmx light."""
        self._state = False
        self._brightness = 0
        self._fixture.dim(self._brightness, self.SMOOTH_MS)

    def update(self, **kwargs: dict[str, Any]) -> None:
        """Update dmx light."""
