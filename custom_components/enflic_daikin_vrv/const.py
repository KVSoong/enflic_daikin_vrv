"""Constants for the enflic_daikin_vrv integration."""

import logging

DOMAIN = "enflic_daikin_vrv"
DEFAULT_SCAN_INTERVAL = 60
LOGGER = logging.getLogger(__package__)

"""Constant required for RESTAPI coordinator."""
CONF_BASE_URL = "base_url"
CONF_DEVELOPER = "developer"
CONF_UPDATE_INTERVAL_IN_SECONDS = "update_inverval_in_seconds"
CONF_GET_DATAPOINT_URL = "get_datapoint_url"

"""Constant required for climate entities"""
CONF_NODES = "nodes"
CONF_NODE_AC_ID = "id"
CONF_NODE_NAME = "name"
CONF_NODE_UNIQUE_ID = "unique_id"
CONF_NODE_AC_MIN_TEMP = "ac_min_temp"
CONF_NODE_AC_MAX_TEMP = "ac_max_temp"
CONF_NODE_SET_STATUS_ON_OFF_URL = "set_status_on_off_url"
CONF_NODE_SET_TEMPERATURE_URL = "set_temperature_url"
CONF_NODE_SET_HVAC_MODE_URL = "set_hvac_mode_url"
CONF_NODE_SET_FAN_MODE_URL = "set_fan_mode_url"
CONF_NODE_SET_SWING_MODE_URL = "set_swing_mode_url"
CONF_NODE_QUERY_KWARG_DEVICE_ID = "query_kwarg_device_id"
CONF_NODE_QUERY_KWARG_COMMAND = "query_kwarg_command"

"""Constant required to parse decoded RESTApi responses."""
CONF_AC_STATUS = "pv_status_decoded"
CONF_AC_HVAC_MODE = "pv_ac_mode_decoded"
CONF_AC_AIR_FLOW_RATE = "pv_air_flow_rate_level_decoded"
CONF_AC_SWING_MODE = "pv_air_direction_decoded"
CONF_AC_CURRENT_TEMPERATURE = "pv_air_temperature"
CONF_AC_TARGET_TEMPERATURE = "sp_air_temperature"
