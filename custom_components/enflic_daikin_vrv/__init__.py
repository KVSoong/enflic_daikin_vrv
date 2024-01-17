"""The enflic_daikin_vrv integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import IntegrationError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_BASE_URL,
    CONF_DEVELOPER,
    CONF_GET_DATAPOINT_URL,
    CONF_UPDATE_INTERVAL_IN_SECONDS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import EnflicDaikinVrvCoordinator

PLATFORMS: list[Platform] = [Platform.CLIMATE]

BASE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL): cv.string,
        vol.Required(CONF_DEVELOPER): cv.string,
        vol.Optional(
            CONF_UPDATE_INTERVAL_IN_SECONDS,
            default=DEFAULT_SCAN_INTERVAL,
        ): cv.string,
        vol.Required(CONF_GET_DATAPOINT_URL): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Any(BASE_SCHEMA),
            ],
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(
    hass: HomeAssistant,
    config: ConfigType,
) -> bool:
    """Set up enflic_daikin_vrv from a config entry."""
    coordinator = EnflicDaikinVrvCoordinator(
        hass=hass,
        base_url=config[DOMAIN][0][CONF_BASE_URL],
        get_datapoint_url=config[DOMAIN][0][CONF_GET_DATAPOINT_URL],
        update_interval_in_second=config[DOMAIN][0].get(
            CONF_UPDATE_INTERVAL_IN_SECONDS
        ),
    )
    if not await coordinator.config_cold_boot():
        raise IntegrationError(
            f"Fail to setup {DOMAIN}. Check gateway connection before retry."
        )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[CONF_DEVELOPER] = coordinator
    return True
