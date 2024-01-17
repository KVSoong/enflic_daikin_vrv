"""Constant for RESTApi responses."""
MOCK_ALL_DATAPOINT_RESPONSE = {
    "SHOWROOM01": {
        "extended_properties": 0,
        "sp_status": False,
        "pv_status": False,
        "pv_status_decoded": "OFF",
        "pv_alarm": False,
        "pv_malfunction_code": 1,
        "sp_ac_mode": 1,
        "pv_ac_mode": 1,
        "pv_ac_mode_decoded": "COOLING",
        "sp_air_direction": 7,
        "pv_air_direction": 7,
        "pv_air_direction_decoded": "AUTO",
        "sp_air_flow_rate_level": 4,
        "pv_air_flow_rate_level": 4,
        "pv_air_flow_rate_level_decoded": "AUTO",
        "pv_air_temperature": 28.5,
        "sp_air_temperature": 24,
        "pv_is_compressor_connected": True,
        "pv_is_ac_fan_operating": False,
        "pv_is_filter_alert": False,
    }
}
MOCK_SERVER_HEALTH_RESPONSE = {
    "host_ip": "172.17.0.2",
    "host_port": 47809,
    "subnet_mask": 16,
    "is_connected": False,
    "packet_count": 16,
    "elapsed_time": 0.33997474100033287,
}
