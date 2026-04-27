"""Salus iT600 gateway API."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable, Awaitable

import aiohttp

from aiohttp import client_exceptions

from .const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_HEAT_IDLE,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_COOL_IDLE,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    PRESET_FOLLOW_SCHEDULE,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
    PRESET_TEMPORARY_HOLD,
    PRESET_ECO,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    TEMP_CELSIUS,
    SUPPORT_OPEN,
    SUPPORT_CLOSE,
    SUPPORT_SET_POSITION,
    FAN_MODE_AUTO,
    FAN_MODE_HIGH,
    FAN_MODE_MEDIUM,
    FAN_MODE_LOW,
    FAN_MODE_OFF
)
from .encryptor import IT600Encryptor
from .exceptions import (
    IT600AuthenticationError,
    IT600CommandError,
    IT600ConnectionError,
)
from .device_models import (
    BINARY_RELAY_MODELS,
    MODEL_FC600,
    SKIPPED_BINARY_SENSOR_MODELS,
    binary_sensor_device_class,
    is_binary_sensor_summary,
    is_sq610_model,
    model_identifier,
    switch_device_class,
)
from .models import GatewayDevice, ClimateDevice, BinarySensorDevice, SwitchDevice, CoverDevice, SensorDevice

_LOGGER = logging.getLogger("salus_it600")

DEFAULT_HOLD_TYPE = 2
DEFAULT_RUNNING_STATE = 0
PARSING_EXCEPTIONS = (KeyError, TypeError, ValueError)
_MISSING_HOLD_TYPE_WARNED: set[str] = set()


def _device_name(device_status: dict[str, Any], unique_id: str | None) -> str:
    """Return a device name from a raw Salus gateway payload."""
    default_name = unique_id or "Unknown"
    raw_name = device_status.get("sZDO", {}).get(
        "DeviceName",
        json.dumps({"deviceName": default_name}),
    )

    try:
        return json.loads(raw_name)["deviceName"]
    except (KeyError, TypeError, ValueError):
        return default_name


def _hold_type(payload: dict[str, Any], unique_id: str) -> int:
    """Return HoldType, defaulting broken payloads to permanent hold."""
    if "HoldType" not in payload and unique_id not in _MISSING_HOLD_TYPE_WARNED:
        _LOGGER.warning(
            "Salus climate device %s is missing HoldType in the gateway payload; "
            "treating it as Permanent Hold so the device can load",
            unique_id,
        )
        _MISSING_HOLD_TYPE_WARNED.add(unique_id)

    return payload.get("HoldType", DEFAULT_HOLD_TYPE)


def _validate_gateway_response(response: Any, context: str) -> dict[str, Any]:
    """Validate that a gateway response is a JSON object with a status field."""
    if not isinstance(response, dict):
        raise IT600CommandError(
            f"Gateway {context} response must be an object, got "
            f"{type(response).__name__}"
        )

    if "status" not in response:
        raise IT600CommandError(
            f"Gateway {context} response is missing 'status'. "
            f"Got keys: {sorted(response)}"
        )

    return response


def _response_items(response: Any, context: str) -> list[dict[str, Any]]:
    """Return and validate the device list from a gateway response."""
    response = _validate_gateway_response(response, context)
    items = response.get("id")
    if not isinstance(items, list):
        raise IT600CommandError(
            f"Gateway {context} response is missing list field 'id'. "
            f"Got keys: {sorted(response)}"
        )

    invalid_indexes = [
        index for index, item in enumerate(items) if not isinstance(item, dict)
    ]
    if invalid_indexes:
        raise IT600CommandError(
            f"Gateway {context} response contains non-object device entries "
            f"at indexes {invalid_indexes}"
        )

    return items


def _device_status_request_items(
    devices: list[Any],
    device_type: str,
) -> list[dict[str, dict[str, Any]]]:
    """Build deviceid request items, skipping malformed discovery entries."""
    request_items = []
    for device in devices:
        data = device.get("data") if isinstance(device, dict) else None
        if not isinstance(data, dict):
            _LOGGER.warning(
                "Skipping %s discovery entry without a data object: %r",
                device_type,
                device,
            )
            continue
        request_items.append({"data": data})

    return request_items


def _online(device_status: dict[str, Any]) -> bool:
    """Return whether a device is marked online in a gateway payload."""
    return device_status.get("sZDOInfo", {}).get("OnlineStatus_i", 1) == 1


def _firmware_version(device_status: dict[str, Any]) -> str | None:
    """Return the common firmware version field from a gateway payload."""
    return device_status.get("sZDO", {}).get("FirmwareVersion")


def _common_device_args(
    device_status: dict[str, Any],
    unique_id: str,
) -> dict[str, Any]:
    """Return constructor args shared by most device models."""
    model = model_identifier(device_status)
    return {
        "available": _online(device_status),
        "name": _device_name(device_status, unique_id),
        "unique_id": unique_id,
        "data": device_status["data"],
        "manufacturer": device_status.get("sBasicS", {}).get(
            "ManufactureName",
            "SALUS",
        ),
        "model": model,
        "sw_version": _firmware_version(device_status),
    }


def _parse_cover_device(device_status: dict[str, Any]) -> CoverDevice | None:
    """Parse one cover device detail payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    if device_status.get("sButtonS", {}).get("Mode") == 0:
        return None

    current_position = device_status.get("sLevelS", {}).get("CurrentLevel")
    move_to_level = device_status.get("sLevelS", {}).get("MoveToLevel_f")
    if move_to_level is not None and len(move_to_level) >= 2:
        set_position = int(move_to_level[:2], 16)
    else:
        set_position = None

    return CoverDevice(
        **_common_device_args(device_status, unique_id),
        current_cover_position=current_position,
        is_opening=None if set_position is None else current_position < set_position,
        is_closing=None if set_position is None else current_position > set_position,
        is_closed=current_position == 0,
        supported_features=SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION,
        device_class=None,
    )


def _parse_switch_device(device_status: dict[str, Any]) -> SwitchDevice | None:
    """Parse one switch device detail payload."""
    base_unique_id = device_status.get("data", {}).get("UniID")
    if base_unique_id is None:
        return None

    unique_id = f"{base_unique_id}_{device_status['data']['Endpoint']}"
    if device_status.get("sLevelS") is not None:
        return None

    is_on = device_status.get("sOnOffS", {}).get("OnOff")
    if is_on is None:
        return None

    model = model_identifier(device_status)
    return SwitchDevice(
        **_common_device_args(device_status, unique_id),
        is_on=is_on == 1,
        device_class=switch_device_class(model),
    )


def _parse_sensor_device(device_status: dict[str, Any]) -> SensorDevice | None:
    """Parse one temperature sensor detail payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    temperature = device_status.get("sTempS", {}).get("MeasuredValue_x100")
    if temperature is None:
        return None

    unique_id = f"{unique_id}_temp"
    return SensorDevice(
        **_common_device_args(device_status, unique_id),
        state=temperature / 100,
        unit_of_measurement=TEMP_CELSIUS,
        device_class="temperature",
    )


def _parse_binary_sensor_device(
    device_status: dict[str, Any],
) -> BinarySensorDevice | None:
    """Parse one binary sensor detail payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    model = model_identifier(device_status)
    if model in SKIPPED_BINARY_SENSOR_MODELS:
        return None

    if model in BINARY_RELAY_MODELS:
        is_on = device_status.get("sIT600I", {}).get("RelayStatus")
    else:
        is_on = device_status.get("sIASZS", {}).get("ErrorIASZSAlarmed1")

    if is_on is None:
        return None

    return BinarySensorDevice(
        **_common_device_args(device_status, unique_id),
        is_on=is_on == 1,
        device_class=binary_sensor_device_class(model),
    )


def _climate_common_args(
    device_status: dict[str, Any],
    unique_id: str,
) -> dict[str, Any]:
    """Return constructor args shared by climate devices."""
    return {
        **_common_device_args(device_status, unique_id),
        "temperature_unit": TEMP_CELSIUS,
        "precision": 0.1,
        "device_class": "temperature",
    }


def _parse_it600th_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    th: dict[str, Any],
) -> ClimateDevice:
    """Parse one standard iT600 thermostat detail payload."""
    model = model_identifier(device_status)
    current_humidity = (
        th.get("SunnySetpoint_x100") if is_sq610_model(model) else None
    )
    hold_type = _hold_type(th, unique_id)
    running_state = th.get("RunningState", DEFAULT_RUNNING_STATE)
    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=current_humidity,
        current_temperature=th["LocalTemperature_x100"] / 100,
        target_temperature=th["HeatingSetpoint_x100"] / 100,
        max_temp=th.get("MaxHeatSetpoint_x100", 3500) / 100,
        min_temp=th.get("MinHeatSetpoint_x100", 500) / 100,
        hvac_mode=HVAC_MODE_OFF
        if hold_type == 7
        else HVAC_MODE_HEAT
        if hold_type == 2
        else HVAC_MODE_AUTO,
        hvac_action=CURRENT_HVAC_OFF
        if hold_type == 7
        else CURRENT_HVAC_IDLE
        if running_state % 2 == 0
        else CURRENT_HVAC_HEAT,
        hvac_modes=[HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO],
        preset_mode=PRESET_OFF
        if hold_type == 7
        else PRESET_PERMANENT_HOLD
        if hold_type == 2
        else PRESET_FOLLOW_SCHEDULE,
        preset_modes=[PRESET_FOLLOW_SCHEDULE, PRESET_PERMANENT_HOLD, PRESET_OFF],
        fan_mode=None,
        fan_modes=None,
        locked=None,
        supported_features=SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE,
    )


def _parse_fan_coil_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    ther: dict[str, Any],
    scomm: dict[str, Any],
    sfans: dict[str, Any],
) -> ClimateDevice:
    """Parse one FC600 fan-coil thermostat detail payload."""
    is_heating = ther["SystemMode"] == 4
    fan_mode = sfans.get("FanMode", 5)
    hold_type = _hold_type(scomm, unique_id)
    running_state = ther.get("RunningState", DEFAULT_RUNNING_STATE)

    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=None,
        current_temperature=ther["LocalTemperature_x100"] / 100,
        target_temperature=(ther["HeatingSetpoint_x100"] / 100)
        if is_heating
        else (ther["CoolingSetpoint_x100"] / 100),
        max_temp=(ther.get("MaxHeatSetpoint_x100", 4000) / 100)
        if is_heating
        else (ther.get("MaxCoolSetpoint_x100", 4000) / 100),
        min_temp=(ther.get("MinHeatSetpoint_x100", 500) / 100)
        if is_heating
        else (ther.get("MinCoolSetpoint_x100", 500) / 100),
        hvac_mode=HVAC_MODE_HEAT
        if ther["SystemMode"] == 4
        else HVAC_MODE_COOL
        if ther["SystemMode"] == 3
        else HVAC_MODE_AUTO,
        hvac_action=CURRENT_HVAC_OFF
        if hold_type == 7
        else CURRENT_HVAC_IDLE
        if running_state == 0
        else CURRENT_HVAC_HEAT
        if is_heating and running_state == 33
        else CURRENT_HVAC_HEAT_IDLE
        if is_heating
        else CURRENT_HVAC_COOL
        if running_state == 66
        else CURRENT_HVAC_COOL_IDLE,
        hvac_modes=[HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO],
        preset_mode=PRESET_OFF
        if hold_type == 7
        else PRESET_PERMANENT_HOLD
        if hold_type == 2
        else PRESET_ECO
        if hold_type == 10
        else PRESET_TEMPORARY_HOLD
        if hold_type == 1
        else PRESET_FOLLOW_SCHEDULE,
        preset_modes=[
            PRESET_OFF,
            PRESET_PERMANENT_HOLD,
            PRESET_ECO,
            PRESET_TEMPORARY_HOLD,
            PRESET_FOLLOW_SCHEDULE,
        ],
        fan_mode=FAN_MODE_OFF
        if fan_mode == 0
        else FAN_MODE_HIGH
        if fan_mode == 3
        else FAN_MODE_MEDIUM
        if fan_mode == 2
        else FAN_MODE_LOW
        if fan_mode == 1
        else FAN_MODE_AUTO,
        fan_modes=[
            FAN_MODE_AUTO,
            FAN_MODE_HIGH,
            FAN_MODE_MEDIUM,
            FAN_MODE_LOW,
            FAN_MODE_OFF,
        ],
        locked=device_status.get("sTherUIS", {}).get("LockKey", 0) == 1,
        supported_features=(
            SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE | SUPPORT_FAN_MODE
        ),
    )


def _parse_climate_device(device_status: dict[str, Any]) -> ClimateDevice | None:
    """Parse one climate device detail payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    th = device_status.get("sIT600TH")
    if isinstance(th, dict):
        return _parse_it600th_climate_device(device_status, unique_id, th)

    ther = device_status.get("sTherS")
    scomm = device_status.get("sComm")
    sfans = device_status.get("sFanS")
    if isinstance(ther, dict) and isinstance(scomm, dict) and isinstance(sfans, dict):
        return _parse_fan_coil_climate_device(
            device_status,
            unique_id,
            ther,
            scomm,
            sfans,
        )

    return None


class IT600Gateway:
    def __init__(
            self,
            euid: str,
            host: str,
            port: int = 80,
            request_timeout: int = 5,
            session: aiohttp.client.ClientSession = None,
            debug: bool = False,
    ):
        self._encryptor = IT600Encryptor(euid)
        self._host = host
        self._port = port
        self._request_timeout = request_timeout
        self._debug = debug
        self._lock = asyncio.Lock()  # Gateway supports very few concurrent requests

        """Initialize connection with the iT600 gateway."""
        self._session = session
        self._close_session = False

        self._gateway_device: Optional[GatewayDevice] = None

        self._climate_devices: Dict[str, ClimateDevice] = {}
        self._climate_update_callbacks: List[Callable[[Any], Awaitable[None]]] = []

        self._binary_sensor_devices: Dict[str, BinarySensorDevice] = {}
        self._binary_sensor_update_callbacks: List[Callable[[Any], Awaitable[None]]] = []

        self._switch_devices: Dict[str, SwitchDevice] = {}
        self._switch_update_callbacks: List[Callable[[Any], Awaitable[None]]] = []

        self._cover_devices: Dict[str, CoverDevice] = {}
        self._cover_update_callbacks: List[Callable[[Any], Awaitable[None]]] = []

        self._sensor_devices: Dict[str, SensorDevice] = {}
        self._sensor_update_callbacks: List[Callable[[Any], Awaitable[None]]] = []

    async def connect(self) -> str:
        """Public method for connecting to Salus universal gateway.
           On successful connection, returns gateway's mac address"""

        _LOGGER.debug("Trying to connect to gateway at %s", self._host)

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            all_devices = await self._make_encrypted_request(
                "read",
                {
                    "requestAttr": "readall"
                }
            )

            gateway = next(
                filter(
                    lambda x: len(x.get("sGateway", {}).get("NetworkLANMAC", "")) > 0,
                    _response_items(all_devices, "gateway discovery"),
                ),
                None,
            )

            if gateway is None:
                raise IT600CommandError(
                    "Error occurred while communicating with iT600 gateway: "
                    "response did not contain gateway information"
                )

            return gateway["sGateway"]["NetworkLANMAC"]
        except IT600ConnectionError as ae:
            try:
                async with asyncio.timeout(self._request_timeout):
                    await self._session.get(f"http://{self._host}:{self._port}/")
            except (asyncio.TimeoutError, client_exceptions.ClientError):
                raise IT600ConnectionError(
                    "Error occurred while communicating with iT600 gateway: "
                    "check if you have specified host/IP address correctly"
                ) from ae

            raise IT600AuthenticationError(
                "Error occurred while communicating with iT600 gateway: "
                "check if you have specified EUID correctly"
            ) from ae

    async def poll_status(self, send_callback=False) -> None:
        """Public method for polling the state of Salus iT600 devices."""

        all_devices = await self._make_encrypted_request(
            "read",
            {
                "requestAttr": "readall"
            }
        )

        device_items = _response_items(all_devices, "readall")

        gateway_devices = list(
            filter(lambda x: "sGateway" in x, device_items)
        )
        await self._refresh_gateway_device(gateway_devices, send_callback)

        climate_devices = list(
            filter(lambda x: ("sIT600TH" in x) or ("sTherS" in x), device_items)
        )
        await self._refresh_climate_devices(climate_devices, send_callback)

        binary_sensors = list(filter(is_binary_sensor_summary, device_items))
        await self._refresh_binary_sensor_devices(binary_sensors, send_callback)

        sensors = list(
            filter(lambda x: "sTempS" in x, device_items)
        )
        await self._refresh_sensor_devices(sensors, send_callback)

        switches = list(
            filter(lambda x: "sOnOffS" in x, device_items)
        )
        await self._refresh_switch_devices(switches, send_callback)

        covers = list(
            filter(lambda x: "sLevelS" in x, device_items)
        )
        await self._refresh_cover_devices(covers, send_callback)

    async def _refresh_device_collection(
        self,
        devices: List[Any],
        device_type: str,
        state_attr: str,
        parser: Callable[[dict[str, Any]], Any | None],
        callback: Callable[..., Awaitable[None]],
        send_callback: bool = False,
    ) -> None:
        """Refresh one device collection using a parser for that device type."""
        local_devices = {}

        if devices:
            request_items = _device_status_request_items(devices, device_type)
            if request_items:
                status = await self._make_encrypted_request(
                    "read",
                    {
                        "requestAttr": "deviceid",
                        "id": request_items
                    }
                )

                for device_status in _response_items(
                    status,
                    f"{device_type} device detail",
                ):
                    unique_id = device_status.get("data", {}).get("UniID")
                    try:
                        device = parser(device_status)
                    except PARSING_EXCEPTIONS:
                        _LOGGER.exception(
                            "Failed to parse %s device %s",
                            device_type,
                            unique_id,
                        )
                        continue

                    if device is None:
                        continue

                    local_devices[device.unique_id] = device

                    if send_callback:
                        getattr(self, state_attr)[device.unique_id] = device
                        await callback(device_id=device.unique_id)

        setattr(self, state_attr, local_devices)
        _LOGGER.debug(
            "Refreshed %s %s devices",
            len(local_devices),
            device_type,
        )

    async def _refresh_gateway_device(self, devices: List[Any], send_callback=False):
        local_device: Optional[GatewayDevice] = None

        if devices:
            request_items = _device_status_request_items(devices, "gateway")
            if not request_items:
                self._gateway_device = local_device
                return

            status = await self._make_encrypted_request(
                "read",
                {
                    "requestAttr": "deviceid",
                    "id": request_items
                }
            )

            for device_status in _response_items(status, "gateway device detail"):
                unique_id = device_status.get("sGateway", {}).get("NetworkLANMAC", None)

                if unique_id is None:
                    continue

                model: Optional[str] = device_status.get("sGateway", {}).get("ModelIdentifier", None)

                try:
                    local_device = GatewayDevice(
                        name=model,
                        unique_id=unique_id,
                        data=device_status["data"],
                        manufacturer=device_status.get("sBasicS", {}).get("ManufactureName", "SALUS"),
                        model=model,
                        sw_version=device_status.get("sOTA", {}).get("OTAFirmwareVersion_d", None)
                    )
                except PARSING_EXCEPTIONS:
                    _LOGGER.exception("Failed to poll gateway %s", unique_id)

            self._gateway_device = local_device
            _LOGGER.debug("Refreshed gateway device")

    async def _refresh_cover_devices(self, devices: List[Any], send_callback=False):
        await self._refresh_device_collection(
            devices,
            "cover",
            "_cover_devices",
            _parse_cover_device,
            self._send_cover_update_callback,
            send_callback,
        )

    async def _refresh_switch_devices(self, devices: List[Any], send_callback=False):
        await self._refresh_device_collection(
            devices,
            "switch",
            "_switch_devices",
            _parse_switch_device,
            self._send_switch_update_callback,
            send_callback,
        )

    async def _refresh_sensor_devices(self, devices: List[Any], send_callback=False):
        await self._refresh_device_collection(
            devices,
            "sensor",
            "_sensor_devices",
            _parse_sensor_device,
            self._send_sensor_update_callback,
            send_callback,
        )

    async def _refresh_binary_sensor_devices(self, devices: List[Any], send_callback=False):
        await self._refresh_device_collection(
            devices,
            "binary sensor",
            "_binary_sensor_devices",
            _parse_binary_sensor_device,
            self._send_binary_sensor_update_callback,
            send_callback,
        )

    async def _refresh_climate_devices(self, devices: List[Any], send_callback=False):
        await self._refresh_device_collection(
            devices,
            "climate",
            "_climate_devices",
            _parse_climate_device,
            self._send_climate_update_callback,
            send_callback,
        )

    async def _send_climate_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        if self._climate_update_callbacks:
            for update_callback in self._climate_update_callbacks:
                await update_callback(device_id=device_id)
        else:
            _LOGGER.error("Callback for climate updates has not been set")

    async def _send_binary_sensor_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        if self._binary_sensor_update_callbacks:
            for update_callback in self._binary_sensor_update_callbacks:
                await update_callback(device_id=device_id)
        else:
            _LOGGER.error("Callback for binary sensor updates has not been set")

    async def _send_switch_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        if self._switch_update_callbacks:
            for update_callback in self._switch_update_callbacks:
                await update_callback(device_id=device_id)
        else:
            _LOGGER.error("Callback for switch updates has not been set")

    async def _send_cover_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        if self._cover_update_callbacks:
            for update_callback in self._cover_update_callbacks:
                await update_callback(device_id=device_id)
        else:
            _LOGGER.error("Callback for cover updates has not been set")

    async def _send_sensor_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        if self._sensor_update_callbacks:
            for update_callback in self._sensor_update_callbacks:
                await update_callback(device_id=device_id)
        else:
            _LOGGER.error("Callback for sensor updates has not been set")

    def get_gateway_device(self) -> Optional[GatewayDevice]:
        """Public method to return gateway device."""

        return self._gateway_device

    def get_climate_devices(self) -> Dict[str, ClimateDevice]:
        """Public method to return the state of all Salus IT600 climate devices."""

        return self._climate_devices

    def get_climate_device(self, device_id: str) -> Optional[ClimateDevice]:
        """Public method to return the state of the specified climate device."""

        return self._climate_devices.get(device_id)

    def get_binary_sensor_devices(self) -> Dict[str, BinarySensorDevice]:
        """Public method to return the state of all Salus IT600 binary sensor devices."""

        return self._binary_sensor_devices

    def get_binary_sensor_device(self, device_id: str) -> Optional[BinarySensorDevice]:
        """Public method to return the state of the specified binary sensor device."""

        return self._binary_sensor_devices.get(device_id)

    def get_switch_devices(self) -> Dict[str, SwitchDevice]:
        """Public method to return the state of all Salus IT600 switch devices."""

        return self._switch_devices

    def get_switch_device(self, device_id: str) -> Optional[SwitchDevice]:
        """Public method to return the state of the specified switch device."""

        return self._switch_devices.get(device_id)

    def get_cover_devices(self) -> Dict[str, CoverDevice]:
        """Public method to return the state of all Salus IT600 cover devices."""

        return self._cover_devices

    def get_cover_device(self, device_id: str) -> Optional[CoverDevice]:
        """Public method to return the state of the specified cover device."""

        return self._cover_devices.get(device_id)

    def get_sensor_devices(self) -> Dict[str, SensorDevice]:
        """Public method to return the state of all Salus IT600 sensor devices."""

        return self._sensor_devices

    def get_sensor_device(self, device_id: str) -> Optional[SensorDevice]:
        """Public method to return the state of the specified sensor device."""

        return self._sensor_devices.get(device_id)

    async def set_cover_position(self, device_id: str, position: int) -> None:
        """Public method to set position/level (where 0 means closed and 100 is fully open) on the specified cover device."""

        if position < 0 or position > 100:
            raise ValueError("position must be between 0 and 100 (both bounds inclusive)")

        device = self.get_cover_device(device_id)

        if device is None:
            _LOGGER.error("Cannot set cover position: cover device not found with the specified id: %s", device_id)
            return

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        "sLevelS": {
                            "SetMoveToLevel": f"{format(position, '02x')}FFFF"
                        },
                    }
                ],
            },
        )

    async def open_cover(self, device_id: str) -> None:
        """Public method to open the specified cover device."""

        await self.set_cover_position(device_id, 100)

    async def close_cover(self, device_id: str) -> None:
        """Public method to close the specified cover device."""

        await self.set_cover_position(device_id, 0)

    async def turn_on_switch_device(self, device_id: str) -> None:
        """Public method to turn on the specified switch device."""

        device = self.get_switch_device(device_id)

        if device is None:
            _LOGGER.error("Cannot turn on: switch device not found with the specified id: %s", device_id)
            return

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        "sOnOffS": {
                            "SetOnOff": 1
                        },
                    }
                ],
            },
        )

    async def turn_off_switch_device(self, device_id: str) -> None:
        """Public method to turn off the specified switch device."""

        device = self.get_switch_device(device_id)

        if device is None:
            _LOGGER.error("Cannot turn off: switch device not found with the specified id: %s", device_id)
            return

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        "sOnOffS": {
                            "SetOnOff": 0
                        },
                    }
                ],
            },
        )

    async def set_climate_device_preset(self, device_id: str, preset: str) -> None:
        """Public method for setting the hvac preset."""

        device = self.get_climate_device(device_id)

        if device is None:
            _LOGGER.error("Cannot set mode: climate device not found with the specified id: %s", device_id)
            return

        if device.model == MODEL_FC600:
            request_data = { "sComm": { "SetHoldType": 7 if preset == PRESET_OFF else 10 if preset == PRESET_ECO else 2 if preset == PRESET_PERMANENT_HOLD else 1 if preset == PRESET_TEMPORARY_HOLD else 0 } }
        else:
            request_data = { "sIT600TH": { "SetHoldType": 7 if preset == PRESET_OFF else 2 if preset == PRESET_PERMANENT_HOLD else 0 } }

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        **request_data,
                    }
                ],
            },
        )

    async def set_climate_device_mode(self, device_id: str, mode: str) -> None:
        """Public method for setting the hvac mode."""

        device = self.get_climate_device(device_id)

        if device is None:
            _LOGGER.error("Cannot set mode: device not found with the specified id: %s", device_id)
            return

        if device.model == MODEL_FC600:
            request_data = { "sTherS": { "SetSystemMode": 4 if mode == HVAC_MODE_HEAT else 3 if mode == HVAC_MODE_COOL else HVAC_MODE_AUTO } }
        else:
            request_data = { "sIT600TH": { "SetHoldType": 7 if mode == HVAC_MODE_OFF else 0 } }

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        **request_data,
                    }
                ],
            },
        )

    async def set_climate_device_fan_mode(self, device_id: str, mode: str) -> None:
        """Public method for setting the hvac fan mode."""

        device = self.get_climate_device(device_id)

        if device is None:
            _LOGGER.error("Cannot set fan mode: device not found with the specified id: %s", device_id)
            return

        request_data = { "sFanS": { "FanMode": 5 if mode == FAN_MODE_AUTO else 3 if mode == FAN_MODE_HIGH else 2 if mode == FAN_MODE_MEDIUM else 1 if mode == FAN_MODE_LOW else 0 } }

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        **request_data,
                    }
                ],
            },
        )

    async def set_climate_device_locked(self, device_id: str, locked: bool) -> None:
        """Public method for setting the hvac locked status."""

        device = self.get_climate_device(device_id)

        if device is None:
            _LOGGER.error("Cannot set locked status: device not found with the specified id: %s", device_id)
            return

        request_data = { "sTherUIS": { "LockKey": 1 if locked else 0 } }

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        **request_data,
                    }
                ],
            },
        )

    async def set_climate_device_temperature(self, device_id: str, setpoint_celsius: float) -> None:
        """Public method for setting the temperature."""

        device = self.get_climate_device(device_id)

        if device is None:
            _LOGGER.error("Cannot set mode: climate device not found with the specified id: %s", device_id)
            return

        if device.model == MODEL_FC600:
          if device.hvac_mode == HVAC_MODE_COOL:
              request_data = { "sTherS": { "SetCoolingSetpoint_x100": int(self.round_to_half(setpoint_celsius) * 100) } }
          else:
              request_data = { "sTherS": { "SetHeatingSetpoint_x100": int(self.round_to_half(setpoint_celsius) * 100) } }
        else:
          request_data = { "sIT600TH": { "SetHeatingSetpoint_x100": int(self.round_to_half(setpoint_celsius) * 100) } }

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        **request_data,
                    }
                ],
            },
        )

    @staticmethod
    def round_to_half(number: float) -> float:
        """Rounds number to half of the integer (eg. 1.01 -> 1, 1.4 -> 1.5, 1.8 -> 2)"""

        return round(number * 2) / 2

    async def add_climate_update_callback(self, method: Callable[[Any], Awaitable[None]]) -> None:
        """Public method to add a climate callback subscriber."""

        self._climate_update_callbacks.append(method)

    async def add_binary_sensor_update_callback(self, method: Callable[[Any], Awaitable[None]]) -> None:
        """Public method to add a binary sensor callback subscriber."""

        self._binary_sensor_update_callbacks.append(method)

    async def add_switch_update_callback(self, method: Callable[[Any], Awaitable[None]]) -> None:
        """Public method to add a switch callback subscriber."""

        self._switch_update_callbacks.append(method)

    async def add_cover_update_callback(self, method: Callable[[Any], Awaitable[None]]) -> None:
        """Public method to add a cover callback subscriber."""

        self._cover_update_callbacks.append(method)

    async def add_sensor_update_callback(self, method: Callable[[Any], Awaitable[None]]) -> None:
        """Public method to add a sensor callback subscriber."""

        self._sensor_update_callbacks.append(method)

    async def _make_encrypted_request(self, command: str, request_body: dict) -> Any:
        """Makes encrypted Salus iT600 json request, decrypts and returns response."""

        async with self._lock:
            if self._session is None:
                self._session = aiohttp.ClientSession()
                self._close_session = True

            try:
                request_url = f"http://{self._host}:{self._port}/deviceid/{command}"
                request_body_json = json.dumps(request_body)

                if self._debug:
                    _LOGGER.debug("Gateway request: POST %s\n%s\n", request_url, request_body_json)

                async with asyncio.timeout(self._request_timeout):
                    resp = await self._session.post(
                        request_url,
                        data=self._encryptor.encrypt(request_body_json),
                        headers={"content-type": "application/json"},
                    )
                    response_bytes = await resp.read()
                    response_json_string = self._encryptor.decrypt(response_bytes)

                    if self._debug:
                        _LOGGER.debug("Gateway response:\n%s\n", response_json_string)

                    response_json = _validate_gateway_response(
                        json.loads(response_json_string),
                        command,
                    )

                    if response_json["status"] != "success":
                        repr_request_body = repr(request_body)
                        repr_response_body = repr(response_json)

                        _LOGGER.error("%s failed: %s", command, repr_request_body)
                        raise IT600CommandError(
                            f"iT600 gateway rejected '{command}' command with content "
                            f"'{repr_request_body}' and response '{repr_response_body}'"
                        )

                    return response_json
            except asyncio.TimeoutError as e:
                _LOGGER.error("Timeout while connecting to gateway: %s", e)
                raise IT600ConnectionError(
                    "Error occurred while communicating with iT600 gateway: timeout"
                ) from e
            except client_exceptions.ClientConnectorError as e:
                raise IT600ConnectionError(
                    "Error occurred while communicating with iT600 gateway: "
                    "check if you have specified host/IP address correctly"
                ) from e
            except client_exceptions.ClientError as e:
                raise IT600ConnectionError(
                    "Error occurred while communicating with iT600 gateway"
                ) from e
            except json.JSONDecodeError as e:
                _LOGGER.error("Gateway returned invalid JSON for %s command", command)
                raise IT600CommandError(
                    "Invalid JSON response received from iT600 gateway"
                ) from e
            except IT600CommandError:
                raise
            except Exception:
                _LOGGER.exception("Unexpected error while communicating with iT600 gateway")
                raise

    async def close(self) -> None:
        """Close open client session."""

        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "IT600Gateway":
        """Async enter."""

        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""

        await self.close()
