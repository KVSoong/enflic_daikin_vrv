"""Support for Enflic Bacnet over RESTApi Gateway for Daikin VRV."""
from __future__ import annotations

from typing import Any, Union

import voluptuous as vol

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    PLATFORM_SCHEMA,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ServiceValidationError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_AC_AIR_FLOW_RATE,
    CONF_AC_CURRENT_TEMPERATURE,
    CONF_AC_HVAC_MODE,
    CONF_AC_STATUS,
    CONF_AC_SWING_MODE,
    CONF_AC_TARGET_TEMPERATURE,
    CONF_DEVELOPER,
    CONF_NODE_AC_ID,
    CONF_NODE_AC_MAX_TEMP,
    CONF_NODE_AC_MIN_TEMP,
    CONF_NODE_NAME,
    CONF_NODE_QUERY_KWARG_COMMAND,
    CONF_NODE_QUERY_KWARG_DEVICE_ID,
    CONF_NODE_SET_FAN_MODE_URL,
    CONF_NODE_SET_HVAC_MODE_URL,
    CONF_NODE_SET_STATUS_ON_OFF_URL,
    CONF_NODE_SET_SWING_MODE_URL,
    CONF_NODE_SET_TEMPERATURE_URL,
    CONF_NODE_UNIQUE_ID,
    CONF_NODES,
    DOMAIN,
)
from .coordinator import EnflicDaikinVrvCoordinator

NODE_SCHEMA = {
    CONF_NODES: [
        {
            vol.Required(CONF_NODE_AC_ID): cv.string,
            vol.Required(CONF_NODE_NAME): cv.string,
            vol.Required(CONF_NODE_UNIQUE_ID): cv.string,
            vol.Optional(CONF_NODE_AC_MIN_TEMP, default=16): int,
            vol.Optional(CONF_NODE_AC_MAX_TEMP, default=30): int,
            vol.Optional(CONF_NODE_SET_STATUS_ON_OFF_URL, default=None): vol.Any(
                None, cv.string
            ),
            vol.Optional(CONF_NODE_SET_TEMPERATURE_URL, default=None): vol.Any(
                None, cv.string
            ),
            vol.Optional(CONF_NODE_SET_HVAC_MODE_URL, default=None): vol.Any(
                None, cv.string
            ),
            vol.Optional(CONF_NODE_SET_FAN_MODE_URL, default=None): vol.Any(
                None, cv.string
            ),
            vol.Optional(CONF_NODE_SET_SWING_MODE_URL, default=None): vol.Any(
                None, cv.string
            ),
            vol.Optional(CONF_NODE_QUERY_KWARG_DEVICE_ID, default=None): vol.Any(
                None, cv.string
            ),
            vol.Optional(CONF_NODE_QUERY_KWARG_COMMAND, default=None): vol.Any(
                None, cv.string
            ),
        }
    ]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    schema=NODE_SCHEMA,
    extra=vol.ALLOW_EXTRA,
)

# HVAC Modes
HA_STATE_TO_DAIKIN = {
    HVACMode.COOL: "COOLING",
    HVACMode.DRY: "DRY",
    HVACMode.FAN_ONLY: "FAN",
    HVACMode.OFF: "OFF",
}
DAIKIN_STATE_TO_HA = {val: key for key, val in HA_STATE_TO_DAIKIN.items()}

# Air flow rate
HA_AIR_FLOW_RATE_TO_DAIKIN = {
    FAN_LOW: "LOW",
    FAN_MEDIUM: "MEDIUM",
    FAN_HIGH: "HIGH",
    FAN_AUTO: "AUTO",
}
DAIKIN_AIR_FLOW_RATE_TO_HA = {
    val: key for key, val in HA_AIR_FLOW_RATE_TO_DAIKIN.items()
}

HA_AIR_DIRECTION_TO_DAIKIN = {
    "LEVEL_1": "LEVEL_1",
    "LEVEL_2": "LEVEL_2",
    "LEVEL_3": "LEVEL_3",
    "LEVEL_4": "LEVEL_4",
    "LEVEL_5": "LEVEL_5",
    "AUTO": "AUTO",
}
DAIKIN_AIR_DIRECTION_TO_HA = {
    val: key for key, val in HA_AIR_DIRECTION_TO_DAIKIN.items()
}


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Daikin Climate entry."""
    coordinator: EnflicDaikinVrvCoordinator = hass.data[DOMAIN][CONF_DEVELOPER]

    entities = []
    for val_config in config[CONF_NODES]:
        if val_config[CONF_NODE_AC_ID] not in coordinator.data:
            raise ConfigEntryError(
                f"AC_ID: [{val_config[CONF_NODE_AC_ID]}] not found is gateway response. Validate the [{CONF_NODE_AC_ID}] key in YAML file"
            )
        entities.append(
            EnflicDaikinClimate(
                coordinator=coordinator,
                device_id=val_config[CONF_NODE_AC_ID],
                device_name=val_config[CONF_NODE_NAME],
                unique_id=val_config[CONF_NODE_UNIQUE_ID],
                min_temp=val_config.get(CONF_NODE_AC_MIN_TEMP),
                max_temp=val_config.get(CONF_NODE_AC_MAX_TEMP),
                set_status_on_off_url=val_config.get(CONF_NODE_SET_STATUS_ON_OFF_URL),
                set_temperature_url=val_config.get(CONF_NODE_SET_TEMPERATURE_URL),
                set_hvac_mode_url=val_config.get(CONF_NODE_SET_HVAC_MODE_URL),
                set_fan_mode_url=val_config.get(CONF_NODE_SET_FAN_MODE_URL),
                set_swing_mode_url=val_config.get(CONF_NODE_SET_SWING_MODE_URL),
                query_kwarg_device_id=val_config.get(CONF_NODE_QUERY_KWARG_DEVICE_ID),
                query_kwarg_command=val_config.get(CONF_NODE_QUERY_KWARG_COMMAND),
            )
        )
    async_add_entities(new_entities=entities, update_before_add=True)


class EnflicDaikinClimate(CoordinatorEntity[EnflicDaikinVrvCoordinator], ClimateEntity):
    """Representation of a Daikin Climate unit."""

    _attr_name: str | None = None
    _attr_hvac_modes = list(HA_STATE_TO_DAIKIN)
    _attr_percision: float = PRECISION_TENTHS
    _attr_translation_key: str = "climate_device"
    _attr_target_temperature_step = 1
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: EnflicDaikinVrvCoordinator,
        device_id: str,
        device_name: Union[str, None] = None,
        unique_id: Union[str, None] = None,
        min_temp: int = 16,
        max_temp: int = 30,
        set_status_on_off_url: Union[str, None] = None,
        set_temperature_url: Union[str, None] = None,
        set_hvac_mode_url: Union[str, None] = None,
        set_fan_mode_url: Union[str, None] = None,
        set_swing_mode_url: Union[str, None] = None,
        query_kwarg_device_id: Union[str, None] = None,
        query_kwarg_command: Union[str, None] = None,
    ) -> None:
        """Initialize Daikin AC Unit."""
        self._coordinator = coordinator
        self._device_id = device_id
        self._attr_name = device_name
        self._attr_unique_id = (
            unique_id
            if unique_id is not None
            else f"{DOMAIN}.{device_id}.{device_name}"
        )
        self._attr_min_temp = min_temp
        self._attr_max_temp = max_temp
        self._set_status_on_off_url = set_status_on_off_url
        self._set_temperature_url = set_temperature_url
        self._set_hvac_mode_url = set_hvac_mode_url
        self._set_fan_mode_url = set_fan_mode_url
        self._set_swing_mode_url = set_swing_mode_url
        self._query_kwarg_device_id = query_kwarg_device_id
        self._query_kwarg_command = query_kwarg_command
        self._attr_supported_features = self.get_features()
        super().__init__(coordinator=coordinator)

    def get_features(self) -> ClimateEntityFeature:
        """Get supported features."""
        features = ClimateEntityFeature(0)
        if self._set_temperature_url is not None:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        if self._set_fan_mode_url is not None:
            features |= ClimateEntityFeature.FAN_MODE
        if self._set_swing_mode_url is not None:
            features |= ClimateEntityFeature.SWING_MODE
        return features

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation setting."""
        ac_status = self._coordinator.data[self._device_id][CONF_AC_STATUS]
        ac_mode = self._coordinator.data[self._device_id][CONF_AC_HVAC_MODE]
        if ac_status == "ON":
            return DAIKIN_STATE_TO_HA[ac_mode]
        return HVACMode.OFF

    @property
    def hvac_modes(self) -> list[HVACMode]:  # pragma: no cover
        """Return the list of available hvac operation modes."""
        hvac_modes = [key for key, val in HA_STATE_TO_DAIKIN.items()]
        return hvac_modes

    @property
    def temperature_unit(self) -> str:  # pragma: no cover
        """Return temperature unit."""
        return UnitOfTemperature.CELSIUS

    @property
    def target_temperature_step(self) -> float | None:  # pragma: no cover
        """Return the supported step of target temperature."""
        return 1

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        fan_mode_decoded: str = self._coordinator.data[self._device_id][
            CONF_AC_AIR_FLOW_RATE
        ]
        return DAIKIN_AIR_FLOW_RATE_TO_HA.get(fan_mode_decoded)

    @property
    def fan_modes(self) -> list[str] | None:  # pragma: no cover
        """Return the list of available fan modes."""
        fan_modes = [key for key, val in HA_AIR_FLOW_RATE_TO_DAIKIN.items()]
        return fan_modes

    @property
    def swing_mode(self) -> str | None:
        """Return the swing setting."""
        swing_mode_decoded: str = self._coordinator.data[self._device_id][
            CONF_AC_SWING_MODE
        ]
        return DAIKIN_AIR_DIRECTION_TO_HA.get(swing_mode_decoded)

    @property
    def swing_modes(self) -> list[str] | None:  # pragma: no cover
        """Return the list of available swing modes."""
        swing_modes = [key for key, val in HA_AIR_DIRECTION_TO_DAIKIN.items()]
        return swing_modes

    @property
    def min_temp(self) -> float:  # pragma: no cover
        """Return the minimum temperature."""
        return self._attr_min_temp

    @property
    def max_temp(self) -> float:  # pragma: no cover
        """Return the maximum temperature."""
        return self._attr_max_temp

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._coordinator.data[self._device_id][CONF_AC_CURRENT_TEMPERATURE]

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._coordinator.data[self._device_id][CONF_AC_TARGET_TEMPERATURE]

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target operation mode."""
        if self._set_status_on_off_url is None or self._set_hvac_mode_url is None:
            raise ServiceValidationError(
                "Current mode doesn't support setting HVAC Mode.",
                translation_domain=DOMAIN,
                translation_key="set_hvac_mode_url_is_none",
            )
        if hvac_mode == HVACMode.OFF:
            await self._coordinator.set_target_value(
                query_route=f"{self._set_status_on_off_url}?{self._query_kwarg_device_id}={self._device_id}&{self._query_kwarg_command}=OFF"
            )
            return
        ac_status = self._coordinator.data[self._device_id][CONF_AC_STATUS]
        if ac_status == "OFF":
            await self._coordinator.set_target_value(
                query_route=f"{self._set_status_on_off_url}?{self._query_kwarg_device_id}={self._device_id}&{self._query_kwarg_command}=ON"
            )
        await self._coordinator.set_target_value(
            query_route=f"{self._set_hvac_mode_url}?{self._query_kwarg_device_id}={self._device_id}&{self._query_kwarg_command}={HA_STATE_TO_DAIKIN.get(hvac_mode)}"
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if self._set_temperature_url is None:
            raise ServiceValidationError(
                "Current mode doesn't support setting Target Temperature.",
                translation_domain=DOMAIN,
                translation_key="set_temperature_url_is_none",
            )
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            raise ServiceValidationError(
                "No target temperature provided",
                translation_domain=DOMAIN,
                translation_key="no_target_temperature",
            )
        if temperature == self.target_temperature:
            return
        await self._coordinator.set_target_value(
            query_route=f"{self._set_temperature_url}?{self._query_kwarg_device_id}={self._device_id}&{self._query_kwarg_command}={temperature}"
        )

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        if self._set_fan_mode_url is None:
            raise ServiceValidationError(
                "Current mode doesn't support setting Fan Level Mode.",
                translation_domain=DOMAIN,
                translation_key="set_fan_mode_url_is_none",
            )
        await self._coordinator.set_target_value(
            query_route=f"{self._set_fan_mode_url}?{self._query_kwarg_device_id}={self._device_id}&{self._query_kwarg_command}={HA_AIR_FLOW_RATE_TO_DAIKIN.get(fan_mode)}"
        )

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing operation."""
        if self._set_swing_mode_url is None:
            raise ServiceValidationError(
                "Current mode doesn't support setting Swing Mode.",
                translation_domain=DOMAIN,
                translation_key="set_swing_mode_url_is_none",
            )
        await self._coordinator.set_target_value(
            query_route=f"{self._set_swing_mode_url}?{self._query_kwarg_device_id}={self._device_id}&{self._query_kwarg_command}={HA_AIR_DIRECTION_TO_DAIKIN.get(swing_mode)}"
        )
