# Daikin VRV Climate Component

---

## Introduction

This hacs integration requires a custom gateway to work, which translates the daikin provided Bacnet server, DMS502B51, to a RESTful API. This integration create native homeassitant climate entity using the URLs from the RESTful API to monitor and control the climate units. 

## Installation with HACS

1. Install hacs to your homeassistant if not already installed following the instruction here, https://hacs.xyz/docs/setup/download/
2. Copy this project directory, https://github.com/KVSoong/enflic_daikin_vrv.
3. Navigate to HACS in HA and select *Integration*.
4. At the top right corner, select the vertical 3 dots and click **Custom repositories**.
5. Paste the link in the `Repository` input field and select **Integration** for the Categeroy dropdown select.
6. Click Add to add this repository to your HA.
7. Once added, you should see this custom repository installed. It should prompt you to restart.
8. Once restarted, you should be able to start configurating the entitiies in the `configuration.yaml` file.

## Configure Coordinator(**REQUIRE**)

Custom coordinator with the gateway setting is required.

1. Paste the following lines to the `configuration.yaml` file.

   ```yaml
   enflic_daikin_vrv:
      base_url: "http://172.17.0.2:7301"    # Update to the correct URL depending on deployment method.
      developer: "enflic"   # Do not change this.
      update_inverval_in_seconds: 10    # Poll frequency in seconds
      get_datapoint_url: "/v1/daikin/fcu/zone/datapoint?zone=all"   # Do not change this.
   ```

## Configure Climate Entities

1. Paste the following code example to the `configuration.yaml` file.

    ```yaml
    climate:
      - platform: enflic_daikin_vrv
        nodes:
        - id: "SHOWROOM01"
          name: "enflic-showroom01"
          unique_id: "enflic-showroom01"
          ac_min_temp: 16
          ac_max_top: 30
          set_status_on_off_url: "/v1/daikin/fcu/sp/status"
          set_temperature_url: "/v1/daikin/fcu/sp/temperature"
          set_hvac_mode_url: "/v1/daikin/fcu/sp/mode"
          set_fan_mode_url: "/v1/daikin/fcu/sp/airflowrate"
          set_swing_mode_url: "/v1/daikin/fcu/sp/airflowdirection"
          query_kwarg_device_id: "fcu"
          query_kwarg_command: "cmd"
    ```

    | Key                       | Required | Description                                       |
    |---------------------------|----------|---------------------------------------------------|
    | id                        | Yes      | Unique identifier for the device. Must reflect from the RESTApi gateway response.  |
    | name                      | Yes      | Name of the device.         |
    | unique_id                 | Yes      | Unique identifier for the device. |
    | ac_min_temp               | Yes      | Minimum temperature supported by the AC.     |
    | ac_max_top                | Yes      | Maximum temperature supported by the AC.     |
    | set_status_on_off_url     | Optional      | URL for setting the AC status (on/off). If not provided, hvac mode setting is disabled |
    | set_temperature_url       | Yes      | URL for setting the target temperature. |
    | set_hvac_mode_url         | Optional      | URL for setting the HVAC mode. If not provided, hvac mode setting is disabled |
    | set_fan_mode_url          | Optional      | URL for setting the fan mode. If not provided, fan level mode setting is disabled |
    | set_swing_mode_url        | Optional      | URL for setting the swing mode. If not provided, swing mode setting is disabled|
    | query_kwarg_device_id     | Yes      | Query parameter key for device identification. |
    | query_kwarg_command       | Yes      | Query parameter key for command identification. |

## Organizing subdirectories for Climate Entities

Will be included in the future.