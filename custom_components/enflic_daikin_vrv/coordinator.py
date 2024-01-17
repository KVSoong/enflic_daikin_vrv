"""Coordinator for Enflic daikin bacnet over REST gateway."""
from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import functools
from typing import Any

from httpx import ConnectError, RequestError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class EnflicDaikinVrvCoordinator(DataUpdateCoordinator):
    """RESTApi Coordinator for custom script."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        get_datapoint_url: str,
        update_interval_in_second: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize Enflic coordinator."""
        self._base_url = base_url
        self.__base_url_get_all_data = f"{base_url}{get_datapoint_url}"
        self.data = dict
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=float(update_interval_in_second)),
        )

    @staticmethod
    def httpx_connection_wrapper(
        func: Callable[..., Any],
    ) -> Callable[..., Any]:
        """Wrap function for all httpx requests."""

        @functools.wraps(func)
        def _wrapper(self, *args: Any, **kwargs: Any) -> Any:
            try:
                vals = func(self, *args, **kwargs)
                return vals
            except RequestError as err:
                raise UpdateFailed(err) from err

        return _wrapper

    @httpx_connection_wrapper
    async def _update_all_data(self) -> dict:
        async with get_async_client(self.hass) as client:
            vals = await client.get(self.__base_url_get_all_data)
            self.data = vals.json() if vals.status_code == 200 else {}
        return self.data

    async def config_cold_boot(self) -> bool:
        """Request to check if gateway is online."""
        try:
            async with get_async_client(self.hass) as client:
                vals = await client.get(f"{self._base_url}/stats/bacnet")
            return vals.is_success
        except ConnectError as err:
            LOGGER.error(f"Connection to daikin_bacnet_restapi gateway error: {err}")
            return False

    @httpx_connection_wrapper
    async def set_target_value(self, query_route: str) -> bool:
        """Set new target value septoint, temperature, hvac mode, swing mode, fan mode."""
        async with get_async_client(self.hass) as client:
            response = await client.put(url=f"{self._base_url}{query_route}")
        if not response.is_success:
            return False
        await self.async_refresh()
        return response.is_success

    async def _async_update_data(self) -> None:
        return await self._update_all_data()
