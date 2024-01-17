"""The test for enflic_daikin_vrv bacnet over restapi climate entity."""
from __future__ import annotations

import asyncio
import copy
import unittest
from unittest.mock import AsyncMock, call

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    HVACMode,
)
from homeassistant.components.enflic_daikin_vrv.climate import EnflicDaikinClimate
from homeassistant.components.enflic_daikin_vrv.const import (
    CONF_AC_AIR_FLOW_RATE,
    CONF_AC_CURRENT_TEMPERATURE,
    CONF_AC_HVAC_MODE,
    CONF_AC_STATUS,
    CONF_AC_SWING_MODE,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.exceptions import ServiceValidationError

from tests.common import MockConfigEntry
from tests.components.enflic_daikin_vrv.const import MOCK_ALL_DATAPOINT_RESPONSE


class TestEnflicDaikinClimateSensor(unittest.TestCase):
    """Test for climate sensor from coordinator data."""

    def setUp(self) -> None:
        """Set up variable for each test cases."""
        self.coordinator = MockConfigEntry(
            domain=DOMAIN,
            data=copy.deepcopy(MOCK_ALL_DATAPOINT_RESPONSE),
            version=1,
            source=SOURCE_USER,
            entry_id="1",
            unique_id="username",
        )
        self.climate_sensor = EnflicDaikinClimate(
            coordinator=self.coordinator,
            device_id="SHOWROOM01",
            device_name="enflic-showroom-01",
            unique_id="enflic-showroom-01",
            min_temp=16,
            max_temp=30,
            set_status_on_off_url="/set/status",
            set_temperature_url="/set/temperature",
            set_hvac_mode_url="/set/hvac/mode",
            set_fan_mode_url="/set/fan/mode",
            set_swing_mode_url="/set/swing/mode",
            query_kwarg_device_id="device_id",
            query_kwarg_command="cmd",
        )

    def tearDown(self) -> None:
        """Clear variables for next test."""
        del self.coordinator
        del self.climate_sensor

    def test_get_features_setup_success(self):
        """Test aircond supported features."""
        self.assertEqual(41, self.climate_sensor._attr_supported_features)

        self.climate_sensor._set_temperature_url = None
        self.climate_sensor._set_fan_mode_url = None
        self.climate_sensor._set_swing_mode_url = None

        # No Features
        self.climate_sensor._attr_supported_features = (
            self.climate_sensor.get_features()
        )
        self.assertEqual(0, self.climate_sensor._attr_supported_features)

        # Temperature Features
        self.climate_sensor._set_temperature_url = "/set/temperature"
        self.climate_sensor._attr_supported_features = (
            self.climate_sensor.get_features()
        )
        self.assertEqual(1, self.climate_sensor._attr_supported_features)

        # Temperature + FAN Mode Features
        self.climate_sensor._set_fan_mode_url = "/set/fan/mode"
        self.climate_sensor._attr_supported_features = (
            self.climate_sensor.get_features()
        )
        self.assertEqual(9, self.climate_sensor._attr_supported_features)

    def test_get_unique_id(self):
        """Test sensor unique id."""
        self.assertEqual("enflic-showroom-01", self.climate_sensor.unique_id)

    def test_get_hvac_mode(self):
        """Test sensor hvac mode."""
        self.assertEqual(HVACMode.OFF, self.climate_sensor.hvac_mode)

        # COOL Mode
        self.coordinator.data[self.climate_sensor._device_id][CONF_AC_STATUS] = "ON"
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_HVAC_MODE
        ] = "COOLING"
        self.assertEqual(HVACMode.COOL, self.climate_sensor.hvac_mode)

        # DRY Mode
        self.coordinator.data[self.climate_sensor._device_id][CONF_AC_HVAC_MODE] = "DRY"
        self.assertEqual(HVACMode.DRY, self.climate_sensor.hvac_mode)

        # FAN Mode
        self.coordinator.data[self.climate_sensor._device_id][CONF_AC_HVAC_MODE] = "FAN"
        self.assertEqual(HVACMode.FAN_ONLY, self.climate_sensor.hvac_mode)

    def test_get_fan_mode(self):
        """Test sensor fan mode."""
        self.assertEqual(FAN_AUTO, self.climate_sensor.fan_mode)

        # LOW Fan Mode
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_AIR_FLOW_RATE
        ] = "LOW"
        self.assertEqual(FAN_LOW, self.climate_sensor.fan_mode)

        # MEDIUM Fan Mode
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_AIR_FLOW_RATE
        ] = "MEDIUM"
        self.assertEqual(FAN_MEDIUM, self.climate_sensor.fan_mode)

        # HIGH Fan Mode
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_AIR_FLOW_RATE
        ] = "HIGH"
        self.assertEqual(FAN_HIGH, self.climate_sensor.fan_mode)

    def test_get_swing_mode(self):
        """Test sensor fan mode."""
        self.assertEqual("AUTO", self.climate_sensor.swing_mode)

        # LEVEL_1 swing direction
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_SWING_MODE
        ] = "LEVEL_1"
        self.assertEqual("LEVEL_1", self.climate_sensor.swing_mode)

        # LEVEL_2 swing direction
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_SWING_MODE
        ] = "LEVEL_2"
        self.assertEqual("LEVEL_2", self.climate_sensor.swing_mode)

        # LEVEL_3 swing direction
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_SWING_MODE
        ] = "LEVEL_3"
        self.assertEqual("LEVEL_3", self.climate_sensor.swing_mode)

        # LEVEL_4 swing direction
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_SWING_MODE
        ] = "LEVEL_4"
        self.assertEqual("LEVEL_4", self.climate_sensor.swing_mode)

        # LEVEL_5 swing direction
        self.coordinator.data[self.climate_sensor._device_id][
            CONF_AC_SWING_MODE
        ] = "LEVEL_5"
        self.assertEqual("LEVEL_5", self.climate_sensor.swing_mode)

    def test_get_current_temperature(self):
        """Test sensor current temperature."""
        self.assertEqual(
            MOCK_ALL_DATAPOINT_RESPONSE[self.climate_sensor._device_id][
                CONF_AC_CURRENT_TEMPERATURE
            ],
            self.climate_sensor.current_temperature,
        )

    def test_async_set_hvac_mode_off(self):
        """Test to change climate sensor hvac mode to off."""
        self.coordinator.set_target_value = AsyncMock()
        url_prefix = f"{self.climate_sensor._set_status_on_off_url}?{self.climate_sensor._query_kwarg_device_id}={self.climate_sensor._device_id}&{self.climate_sensor._query_kwarg_command}="

        # HVAC Mode OFF
        asyncio.get_event_loop().run_until_complete(
            future=self.climate_sensor.async_set_hvac_mode(hvac_mode=HVACMode.OFF),
        )
        self.coordinator.set_target_value.assert_called_once_with(
            query_route=f"{url_prefix}OFF"
        )

    def test_async_set_hvac_mode_cool(self):
        """Test to change climate sensor hvac mode to cool if ac is off."""
        self.coordinator.set_target_value = AsyncMock()
        self.climate_sensor._coordinator.data[self.climate_sensor._device_id][
            CONF_AC_STATUS
        ] = "OFF"
        url_prefix_status = f"{self.climate_sensor._set_status_on_off_url}?{self.climate_sensor._query_kwarg_device_id}={self.climate_sensor._device_id}&{self.climate_sensor._query_kwarg_command}="
        url_prefix_hvac_mode = f"{self.climate_sensor._set_hvac_mode_url}?{self.climate_sensor._query_kwarg_device_id}={self.climate_sensor._device_id}&{self.climate_sensor._query_kwarg_command}="

        # HVAC Mode ON
        asyncio.get_event_loop().run_until_complete(
            future=self.climate_sensor.async_set_hvac_mode(hvac_mode=HVACMode.COOL),
        )
        self.coordinator.set_target_value.assert_has_calls(
            [
                call(query_route=f"{url_prefix_status}ON"),
                call(query_route=f"{url_prefix_hvac_mode}COOLING"),
            ]
        )

    def test_async_set_hvac_mode_disabled(self):
        """Test to change climate sensor hvac mode feature disabled."""
        self.climate_sensor._set_hvac_mode_url = None
        with self.assertRaises(ServiceValidationError):
            asyncio.get_event_loop().run_until_complete(
                future=self.climate_sensor.async_set_hvac_mode(hvac_mode=HVACMode.COOL),
            )

    def test_async_set_target_temperature_success(self):
        """Test to change climate sensor target temperature success."""
        self.coordinator.set_target_value = AsyncMock()
        url_prefix = f"{self.climate_sensor._set_temperature_url}?{self.climate_sensor._query_kwarg_device_id}={self.climate_sensor._device_id}&{self.climate_sensor._query_kwarg_command}="

        asyncio.get_event_loop().run_until_complete(
            future=self.climate_sensor.async_set_temperature(temperature=16),
        )
        self.coordinator.set_target_value.assert_called_once_with(
            query_route=f"{url_prefix}16"
        )

    def test_async_set_target_temperature_same_target_value(self):
        """Test to change climate sensor target temperature success."""
        self.coordinator.set_target_value = AsyncMock()

        asyncio.get_event_loop().run_until_complete(
            future=self.climate_sensor.async_set_temperature(
                temperature=self.climate_sensor.target_temperature
            ),
        )
        self.coordinator.set_target_value.assert_not_called()

    def test_async_set_target_temperature_disabled(self):
        """Test to change climate sensor target temperature feature disabled."""
        self.coordinator.set_target_value = AsyncMock()
        self.climate_sensor._set_temperature_url = None

        with self.assertRaises(ServiceValidationError):
            asyncio.get_event_loop().run_until_complete(
                future=self.climate_sensor.async_set_temperature(temperature=16),
            )

    def test_async_set_target_temperature_kwargs_error(self):
        """Test to change climate sensor target temperature url disabled."""
        self.coordinator.set_target_value = AsyncMock()

        with self.assertRaises(ServiceValidationError):
            asyncio.get_event_loop().run_until_complete(
                future=self.climate_sensor.async_set_temperature(mock=16),
            )

    def test_async_set_fan_mode_success(self):
        """Test to change climate sensor fan mode success."""
        self.coordinator.set_target_value = AsyncMock()
        url_prefix = f"{self.climate_sensor._set_fan_mode_url}?{self.climate_sensor._query_kwarg_device_id}={self.climate_sensor._device_id}&{self.climate_sensor._query_kwarg_command}="

        asyncio.get_event_loop().run_until_complete(
            future=self.climate_sensor.async_set_fan_mode(fan_mode=FAN_AUTO),
        )
        self.coordinator.set_target_value.assert_called_once_with(
            query_route=f"{url_prefix}AUTO"
        )

    def test_async_set_fan_mode_disabled(self):
        """Test to change climate sensor fan mode feature disabled."""
        self.coordinator.set_target_value = AsyncMock()
        self.climate_sensor._set_fan_mode_url = None

        with self.assertRaises(ServiceValidationError):
            asyncio.get_event_loop().run_until_complete(
                future=self.climate_sensor.async_set_fan_mode(fan_mode=FAN_AUTO),
            )

    def test_async_set_swing_mode_success(self):
        """Test to change climate sensor swing mode success."""
        self.coordinator.set_target_value = AsyncMock()
        url_prefix = f"{self.climate_sensor._set_swing_mode_url}?{self.climate_sensor._query_kwarg_device_id}={self.climate_sensor._device_id}&{self.climate_sensor._query_kwarg_command}="

        asyncio.get_event_loop().run_until_complete(
            future=self.climate_sensor.async_set_swing_mode(swing_mode="AUTO"),
        )
        self.coordinator.set_target_value.assert_called_once_with(
            query_route=f"{url_prefix}AUTO"
        )

    def test_async_set_swing_mode_disabled(self):
        """Test to change climate sensor swing mode feature disabled."""
        self.coordinator.set_target_value = AsyncMock()
        self.climate_sensor._set_swing_mode_url = None

        with self.assertRaises(ServiceValidationError):
            asyncio.get_event_loop().run_until_complete(
                future=self.climate_sensor.async_set_swing_mode(swing_mode="AUTO"),
            )
