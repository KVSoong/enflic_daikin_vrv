"""The test for enflic_daikin_bacnet_restapi coordinator."""
from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from homeassistant.components.enflic_daikin_vrv.const import DOMAIN
from homeassistant.components.enflic_daikin_vrv.coordinator import (
    EnflicDaikinVrvCoordinator,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.components.enflic_daikin_vrv.const import MOCK_ALL_DATAPOINT_RESPONSE


@pytest.mark.asyncio
@patch(
    "homeassistant.helpers.httpx_client.httpx.AsyncClient.get",
    return_value=httpx.Response(200, json=MOCK_ALL_DATAPOINT_RESPONSE.copy()),
)
async def test_update_all_data(mock_response, hass: HomeAssistant):
    """Tests to check successful data refresh."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data={"CONF": {"123"}},
        entry_id="1",
        unique_id="username",
        version=2,
    )
    config_entry.add_to_hass(hass)
    mock_coordinator = EnflicDaikinVrvCoordinator(
        hass=hass,
        base_url="http://localhost:7301",
        get_datapoint_url="/get_all",
    )
    result = await mock_coordinator._update_all_data()
    assert result == MOCK_ALL_DATAPOINT_RESPONSE
    mock_response.assert_called_once()


@pytest.mark.asyncio
@patch(
    "homeassistant.helpers.httpx_client.httpx.AsyncClient.get",
    return_value=httpx.Response(
        200, json={"id": "9ed7dasdasd-08ff-4ae1-8952-37e3a323eb08"}
    ),
)
async def test_config_cold_boot_success(mock_response, hass: HomeAssistant):
    """Test to check gateway is reachable on boot."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data={"CONF": {"123"}},
        entry_id="1",
        unique_id="username",
        version=2,
    )
    config_entry.add_to_hass(hass)

    mock_coordinator = EnflicDaikinVrvCoordinator(
        hass=hass,
        base_url="http://localhost:7301",
        get_datapoint_url="/get_all",
    )
    result = await mock_coordinator.config_cold_boot()
    assert result


@pytest.mark.asyncio
@patch(
    "homeassistant.helpers.httpx_client.httpx.AsyncClient.get",
    side_effect=httpx.ConnectError("Failed to connect to gateway."),
)
async def test_config_cold_boot_failure(mock_response, hass: HomeAssistant):
    """Test to handle if gateway is offline on boot."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data={"CONF": {"123"}},
        entry_id="1",
        unique_id="username",
        version=2,
    )
    config_entry.add_to_hass(hass)

    mock_coordinator = EnflicDaikinVrvCoordinator(
        hass=hass,
        base_url="http://localhost:7301",
        get_datapoint_url="/get_all",
    )
    result = await mock_coordinator.config_cold_boot()
    assert result is False
    mock_response.assert_called_once()


@pytest.mark.asyncio
@patch(
    "homeassistant.helpers.httpx_client.httpx.AsyncClient.put",
    return_value=httpx.Response(200, json={"status": True}),
)
@patch(
    "homeassistant.components.enflic_daikin_vrv.EnflicDaikinVrvCoordinator._async_update_data",
    return_value=True,
)
async def test_set_target_value_success(
    mock_refresh,
    mock_response,
    hass: HomeAssistant,
):
    """Test to requests setpoint value change success."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data={"CONF": {"123"}},
        entry_id="1",
        unique_id="username",
        version=2,
    )
    config_entry.add_to_hass(hass)

    mock_coordinator = EnflicDaikinVrvCoordinator(
        hass=hass,
        base_url="http://localhost:7301",
        get_datapoint_url="/get_all",
    )
    await mock_coordinator.set_target_value(query_route="/set")
    mock_response.assert_called_once()
    mock_refresh.assert_called_once()


@pytest.mark.asyncio
@patch(
    "homeassistant.helpers.httpx_client.httpx.AsyncClient.put",
    side_effect=httpx.RequestError("Request error from unittest"),
)
async def test_set_target_value_failure(
    mock_response,
    hass: HomeAssistant,
):
    """Test to requests setpoint value change failure."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data={"CONF": {"123"}},
        entry_id="1",
        unique_id="username",
        version=2,
    )
    config_entry.add_to_hass(hass)

    mock_coordinator = EnflicDaikinVrvCoordinator(
        hass=hass,
        base_url="http://localhost:7301",
        get_datapoint_url="/get_all",
    )
    with pytest.raises(httpx.RequestError):
        result = await mock_coordinator.set_target_value(query_route="/set")
        assert result is False
    mock_response.assert_called_once()
