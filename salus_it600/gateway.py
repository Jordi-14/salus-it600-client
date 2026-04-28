"""Salus iT600 gateway API."""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, TypeVar

import aiohttp

from aiohttp import client_exceptions

from .const import (
    COVER_POSITION_MAX,
    COVER_POSITION_MIN,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_OFF,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
    PRESET_TEMPORARY_HOLD,
    PRESET_ECO,
    FAN_MODE_AUTO,
    FAN_MODE_HIGH,
    FAN_MODE_MEDIUM,
    FAN_MODE_LOW,
    FanMode,
    HoldType,
    SystemMode,
    TEMPERATURE_SCALE,
)
from ._device_parsers import (
    PARSING_EXCEPTIONS,
    parse_binary_sensor_device,
    parse_climate_device,
    parse_cover_device,
    parse_sensor_device,
    parse_switch_device,
)
from .encryptor import IT600Encryptor
from .exceptions import (
    IT600AuthenticationError,
    IT600CommandError,
    IT600ConnectionError,
)
from .device_models import (
    MODEL_FC600,
    is_binary_sensor_summary,
    is_sq610_model,
)
from .models import (
    GatewayDevice,
    ClimateDevice,
    BinarySensorDevice,
    SwitchDevice,
    CoverDevice,
    SensorDevice,
)

_LOGGER = logging.getLogger("salus_it600")

DEVICE_NOT_FOUND_ERROR = "{device_type} device not found with id: {device_id}"
DeviceT = TypeVar(
    "DeviceT",
    ClimateDevice,
    BinarySensorDevice,
    SwitchDevice,
    CoverDevice,
    SensorDevice,
)
UpdateCallback = Callable[..., Awaitable[None]]


def _validate_non_empty_string(value: str, field_name: str) -> str:
    """Validate a public string argument and return its stripped value."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")

    return normalized


def _validate_positive_number(value: int | float, field_name: str) -> int | float:
    """Validate a positive numeric argument."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return value


def _validate_int_range(
    value: int,
    field_name: str,
    min_value: int,
    max_value: int,
) -> int:
    """Validate an integer argument against inclusive bounds."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if value < min_value or value > max_value:
        raise ValueError(
            f"{field_name} must be between {min_value} and {max_value} "
            "(both bounds inclusive)"
        )
    return value


def _validate_supported_value(
    value: str,
    field_name: str,
    supported_values: Sequence[str] | None,
) -> str:
    """Validate that a string argument is supported by the target device."""
    normalized = _validate_non_empty_string(value, field_name)
    if supported_values is not None and normalized not in supported_values:
        raise ValueError(
            f"{field_name} must be one of {sorted(supported_values)}, got "
            f"{normalized!r}"
        )
    return normalized


def _validate_setpoint(
    value: int | float,
    min_temp: float,
    max_temp: float,
) -> float:
    """Validate a temperature setpoint against the device-supported range."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("setpoint_celsius must be a number")

    setpoint = float(value)
    if setpoint < min_temp or setpoint > max_temp:
        raise ValueError(f"setpoint_celsius must be between {min_temp} and {max_temp}")
    return setpoint


def _validate_callback(method: UpdateCallback) -> UpdateCallback:
    """Validate update callback registration input."""
    if not callable(method):
        raise TypeError("method must be callable")
    return method


async def _notify_update_callbacks(
    callbacks: Sequence[UpdateCallback],
    device_id: str,
) -> None:
    """Notify registered update callbacks for one refreshed device."""
    for update_callback in callbacks:
        await update_callback(device_id=device_id)


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


def _flatten_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested gateway payload dictionaries into a single key/value map."""
    flattened: dict[str, Any] = {}

    def _walk(value: Any) -> None:
        if not isinstance(value, dict):
            return

        for nested_key, nested_value in value.items():
            if isinstance(nested_value, dict):
                _walk(nested_value)
            else:
                flattened[nested_key] = nested_value

    _walk(data)
    return flattened


class IT600Gateway:
    """Async client for one Salus UG600 local gateway."""

    def __init__(
        self,
        euid: str,
        host: str,
        port: int = 80,
        request_timeout: int | float = 5,
        session: aiohttp.ClientSession | None = None,
        debug: bool = False,
    ) -> None:
        """Create a gateway client.

        Args:
            euid: Gateway EUID printed on the gateway label, or the fallback
                zero EUID accepted by some installations.
            host: Gateway hostname or local IP address.
            port: Local gateway HTTP port.
            request_timeout: Per-request timeout in seconds.
            session: Optional externally managed aiohttp session.
            debug: Log raw encrypted-command JSON before encryption and after
                decryption.
        """
        euid = _validate_non_empty_string(euid, "euid")
        host = _validate_non_empty_string(host, "host")
        port = _validate_int_range(port, "port", 1, 65535)
        request_timeout = _validate_positive_number(
            request_timeout,
            "request_timeout",
        )

        self._encryptor = IT600Encryptor(euid)
        self._host = host
        self._port = port
        self._request_timeout = request_timeout
        self._debug = debug
        self._lock = asyncio.Lock()  # Gateway supports very few concurrent requests

        self._session = session
        self._close_session = False

        self._gateway_device: GatewayDevice | None = None

        self._climate_devices: dict[str, ClimateDevice] = {}
        self._climate_update_callbacks: list[UpdateCallback] = []

        self._binary_sensor_devices: dict[str, BinarySensorDevice] = {}
        self._binary_sensor_update_callbacks: list[UpdateCallback] = []

        self._switch_devices: dict[str, SwitchDevice] = {}
        self._switch_update_callbacks: list[UpdateCallback] = []

        self._cover_devices: dict[str, CoverDevice] = {}
        self._cover_update_callbacks: list[UpdateCallback] = []

        self._sensor_devices: dict[str, SensorDevice] = {}
        self._sensor_update_callbacks: list[UpdateCallback] = []

    async def connect(self) -> str:
        """Validate gateway access and return the gateway MAC address.

        Raises:
            IT600ConnectionError: If the gateway cannot be reached.
            IT600AuthenticationError: If the gateway answers but rejects the
                encrypted request, usually due to an invalid EUID.
            IT600CommandError: If the gateway response has no gateway device.
        """

        _LOGGER.debug("Trying to connect to gateway at %s", self._host)

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            all_devices = await self._make_encrypted_request(
                "read", {"requestAttr": "readall"}
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

            gateway_mac = gateway["sGateway"]["NetworkLANMAC"]
            if not isinstance(gateway_mac, str):
                raise IT600CommandError(
                    "Gateway discovery response contained an invalid MAC address"
                )
            return gateway_mac
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

    async def poll_status(self, send_callback: bool = False) -> None:
        """Refresh all known device collections from the gateway.

        The method performs a `readall` discovery request, then detailed
        `deviceid` requests for each supported device family. Invalid individual
        devices are logged and skipped; gateway communication errors propagate
        to the caller.
        """

        all_devices = await self._make_encrypted_request(
            "read", {"requestAttr": "readall"}
        )

        device_items = _response_items(all_devices, "readall")

        gateway_devices = list(filter(lambda x: "sGateway" in x, device_items))
        await self._refresh_gateway_device(gateway_devices, send_callback)

        climate_devices = list(
            filter(lambda x: ("sIT600TH" in x) or ("sTherS" in x), device_items)
        )
        await self._refresh_climate_devices(climate_devices, send_callback)

        binary_sensors = list(filter(is_binary_sensor_summary, device_items))
        await self._refresh_binary_sensor_devices(binary_sensors, send_callback)

        sensors = list(filter(lambda x: "sTempS" in x, device_items))
        await self._refresh_sensor_devices(sensors, send_callback)

        switches = list(filter(lambda x: "sOnOffS" in x, device_items))
        await self._refresh_switch_devices(switches, send_callback)

        covers = list(filter(lambda x: "sLevelS" in x, device_items))
        await self._refresh_cover_devices(covers, send_callback)

    async def _refresh_device_collection(
        self,
        devices: list[Any],
        device_type: str,
        state_attr: str,
        parser: Callable[[dict[str, Any]], Any | None],
        callback: UpdateCallback,
        send_callback: bool = False,
    ) -> None:
        """Refresh one device collection using a parser for that device type.

        This is the consolidated pipeline for all device type refreshes. It:
        1. Checks if there are devices of this type to poll
        2. Makes encrypted gateway request for device details
        3. Validates response structure
        4. Parses each device using the provided parser function
        5. Skips devices that return None (invalid or filtered out)
        6. Catches parsing errors, logs them, and continues
        7. Stores device state in internal dict (gateway._<type>_devices)
        8. Optionally triggers update callbacks

        This consolidation eliminates ~60% code duplication across the original
        separate _refresh_*_devices methods while keeping device-type-specific
        logic isolated in parser functions.

        Args:
            devices: List of device summary dicts from readall response
            device_type: Human-readable name for logging (e.g. "switch", "cover")
            state_attr: Internal gateway attribute name (e.g. "_switch_devices")
            parser: Function that parses device_status dict -> Device model or None.
                    Should catch and re-raise PARSING_EXCEPTIONS, or return None
                    for intentionally filtered devices (e.g. disabled endpoints).
            callback: Async callback function to invoke if send_callback=True.
                      Called with device_id argument.
            send_callback: If True, invoke callback for each parsed device.
                          Usually False during poll_status (callback sent once
                          after all types polled), True during discovery.

        Raises:
            IT600ConnectionError: If gateway request fails (propagates up)
            IT600CommandError: If response validation fails

        Example:
            To add a new device type (e.g. "dimmer"):
            1. Add parser function `_parse_dimmer_device()`
            2. Add filter in `poll_status()` to find dimmer devices
            3. Call `_refresh_device_collection()` with the filter results
        """
        local_devices = {}

        if devices:
            request_items = _device_status_request_items(devices, device_type)
            if request_items:
                status = await self._make_encrypted_request(
                    "read", {"requestAttr": "deviceid", "id": request_items}
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

    async def _refresh_gateway_device(
        self,
        devices: list[Any],
        send_callback: bool = False,
    ) -> None:
        local_device: GatewayDevice | None = None

        if devices:
            request_items = _device_status_request_items(devices, "gateway")
            if not request_items:
                self._gateway_device = local_device
                return

            status = await self._make_encrypted_request(
                "read", {"requestAttr": "deviceid", "id": request_items}
            )

            for device_status in _response_items(status, "gateway device detail"):
                unique_id = device_status.get("sGateway", {}).get("NetworkLANMAC", None)

                if unique_id is None:
                    continue

                model: str | None = device_status.get("sGateway", {}).get(
                    "ModelIdentifier", None
                )

                try:
                    local_device = GatewayDevice(
                        name=model or unique_id,
                        unique_id=unique_id,
                        data=device_status["data"],
                        manufacturer=device_status.get("sBasicS", {}).get(
                            "ManufactureName", "SALUS"
                        ),
                        model=model,
                        sw_version=device_status.get("sOTA", {}).get(
                            "OTAFirmwareVersion_d", None
                        ),
                    )
                except PARSING_EXCEPTIONS:
                    _LOGGER.exception("Failed to poll gateway %s", unique_id)

            self._gateway_device = local_device
            _LOGGER.debug("Refreshed gateway device")

    async def _refresh_cover_devices(
        self,
        devices: list[Any],
        send_callback: bool = False,
    ) -> None:
        await self._refresh_device_collection(
            devices,
            "cover",
            "_cover_devices",
            parse_cover_device,
            self._send_cover_update_callback,
            send_callback,
        )

    async def _refresh_switch_devices(
        self,
        devices: list[Any],
        send_callback: bool = False,
    ) -> None:
        await self._refresh_device_collection(
            devices,
            "switch",
            "_switch_devices",
            parse_switch_device,
            self._send_switch_update_callback,
            send_callback,
        )

    async def _refresh_sensor_devices(
        self,
        devices: list[Any],
        send_callback: bool = False,
    ) -> None:
        await self._refresh_device_collection(
            devices,
            "sensor",
            "_sensor_devices",
            parse_sensor_device,
            self._send_sensor_update_callback,
            send_callback,
        )

    async def _refresh_binary_sensor_devices(
        self,
        devices: list[Any],
        send_callback: bool = False,
    ) -> None:
        await self._refresh_device_collection(
            devices,
            "binary sensor",
            "_binary_sensor_devices",
            parse_binary_sensor_device,
            self._send_binary_sensor_update_callback,
            send_callback,
        )

    async def _refresh_climate_devices(
        self,
        devices: list[Any],
        send_callback: bool = False,
    ) -> None:
        await self._refresh_device_collection(
            devices,
            "climate",
            "_climate_devices",
            parse_climate_device,
            self._send_climate_update_callback,
            send_callback,
        )

    async def _send_climate_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        await _notify_update_callbacks(self._climate_update_callbacks, device_id)

    async def _send_binary_sensor_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        await _notify_update_callbacks(
            self._binary_sensor_update_callbacks,
            device_id,
        )

    async def _send_switch_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        await _notify_update_callbacks(self._switch_update_callbacks, device_id)

    async def _send_cover_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        await _notify_update_callbacks(self._cover_update_callbacks, device_id)

    async def _send_sensor_update_callback(self, device_id: str) -> None:
        """Internal method to notify all update callback subscribers."""

        await _notify_update_callbacks(self._sensor_update_callbacks, device_id)

    @staticmethod
    def _validate_device_id(device_id: str) -> str:
        return _validate_non_empty_string(device_id, "device_id")

    def _require_device(
        self,
        device_id: str,
        devices: Mapping[str, DeviceT],
        device_type: str,
    ) -> DeviceT:
        device_id = self._validate_device_id(device_id)
        device = devices.get(device_id)
        if device is None:
            raise KeyError(
                DEVICE_NOT_FOUND_ERROR.format(
                    device_type=device_type,
                    device_id=device_id,
                )
            )
        return device

    def get_gateway_device(self) -> GatewayDevice | None:
        """Return the cached gateway device, if `poll_status()` has found it."""

        return self._gateway_device

    def get_climate_devices(self) -> dict[str, ClimateDevice]:
        """Return cached climate devices keyed by unique device ID."""

        return self._climate_devices

    def get_climate_device(self, device_id: str) -> ClimateDevice | None:
        """Return one cached climate device, or None if it is not loaded."""

        device_id = self._validate_device_id(device_id)
        return self._climate_devices.get(device_id)

    def get_binary_sensor_devices(self) -> dict[str, BinarySensorDevice]:
        """Return cached binary sensor devices keyed by unique device ID."""

        return self._binary_sensor_devices

    def get_binary_sensor_device(self, device_id: str) -> BinarySensorDevice | None:
        """Return one cached binary sensor device, or None if it is not loaded."""

        device_id = self._validate_device_id(device_id)
        return self._binary_sensor_devices.get(device_id)

    def get_switch_devices(self) -> dict[str, SwitchDevice]:
        """Return cached switch devices keyed by unique device ID."""

        return self._switch_devices

    def get_switch_device(self, device_id: str) -> SwitchDevice | None:
        """Return one cached switch device, or None if it is not loaded."""

        device_id = self._validate_device_id(device_id)
        return self._switch_devices.get(device_id)

    def get_cover_devices(self) -> dict[str, CoverDevice]:
        """Return cached cover devices keyed by unique device ID."""

        return self._cover_devices

    def get_cover_device(self, device_id: str) -> CoverDevice | None:
        """Return one cached cover device, or None if it is not loaded."""

        device_id = self._validate_device_id(device_id)
        return self._cover_devices.get(device_id)

    def get_sensor_devices(self) -> dict[str, SensorDevice]:
        """Return cached sensor devices keyed by unique device ID."""

        return self._sensor_devices

    def get_sensor_device(self, device_id: str) -> SensorDevice | None:
        """Return one cached sensor device, or None if it is not loaded."""

        device_id = self._validate_device_id(device_id)
        return self._sensor_devices.get(device_id)

    async def fetch_sq610_properties(
        self,
        device_ids: Sequence[str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Fetch flattened raw gateway properties for cached SQ610 devices.

        Args:
            device_ids: Optional SQ610 climate device IDs. When omitted, all
                cached SQ610 climate devices are fetched.

        Raises:
            KeyError: If a requested device is not in the climate cache.
            ValueError: If a requested device is not an SQ610 model.
            IT600ConnectionError: If the gateway cannot be reached.
            IT600CommandError: If the gateway response is invalid or rejected.
        """
        if isinstance(device_ids, str):
            raise TypeError("device_ids must be a sequence of strings, not a string")

        if device_ids is None:
            devices = [
                device
                for device in self._climate_devices.values()
                if is_sq610_model(device.model)
            ]
        else:
            devices = []
            for device_id in device_ids:
                device = self._require_device(
                    device_id,
                    self._climate_devices,
                    "climate",
                )
                if not is_sq610_model(device.model):
                    raise ValueError(f"climate device {device_id!r} is not an SQ610")
                devices.append(device)

        if not devices:
            return {}

        response = await self._make_encrypted_request(
            "read",
            {
                "requestAttr": "deviceid",
                "id": [{"data": device.data} for device in devices],
            },
        )

        raw_properties: dict[str, dict[str, Any]] = {}
        for device_status in _response_items(response, "SQ610 device detail"):
            unique_id = device_status.get("data", {}).get("UniID")
            if isinstance(unique_id, str):
                raw_properties[unique_id] = _flatten_dict(device_status)

        return raw_properties

    async def write_sq610_property(
        self,
        device_id: str,
        prop: str,
        value: int,
    ) -> None:
        """Write one raw SQ610 `sIT600TH` property.

        This intentionally exposes only the SQ610 write path currently required
        by Home Assistant instead of making the full encrypted request API
        public.
        """
        device = self._require_device(device_id, self._climate_devices, "climate")
        if not is_sq610_model(device.model):
            raise ValueError(f"climate device {device_id!r} is not an SQ610")

        prop = _validate_non_empty_string(prop, "prop")
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("value must be an integer")

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        "sIT600TH": {prop: int(value)},
                    }
                ],
            },
        )

    async def set_cover_position(self, device_id: str, position: int) -> None:
        """Move a cover to a position where 0 is closed and 100 is open."""

        position = _validate_int_range(
            position,
            "position",
            COVER_POSITION_MIN,
            COVER_POSITION_MAX,
        )
        device = self._require_device(device_id, self._cover_devices, "cover")

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        "sLevelS": {"SetMoveToLevel": f"{format(position, '02x')}FFFF"},
                    }
                ],
            },
        )

    async def open_cover(self, device_id: str) -> None:
        """Open a cover fully."""

        await self.set_cover_position(device_id, COVER_POSITION_MAX)

    async def close_cover(self, device_id: str) -> None:
        """Close a cover fully."""

        await self.set_cover_position(device_id, COVER_POSITION_MIN)

    async def turn_on_switch_device(self, device_id: str) -> None:
        """Turn on a switch or relay device."""

        device = self._require_device(device_id, self._switch_devices, "switch")

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        "sOnOffS": {"SetOnOff": 1},
                    }
                ],
            },
        )

    async def turn_off_switch_device(self, device_id: str) -> None:
        """Turn off a switch or relay device."""

        device = self._require_device(device_id, self._switch_devices, "switch")

        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [
                    {
                        "data": device.data,
                        "sOnOffS": {"SetOnOff": 0},
                    }
                ],
            },
        )

    async def set_climate_device_preset(self, device_id: str, preset: str) -> None:
        """Set a climate preset/hold mode supported by the target device."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        preset = _validate_supported_value(preset, "preset", device.preset_modes)
        request_data: dict[str, dict[str, int]]

        if device.model == MODEL_FC600:
            request_data = {
                "sComm": {
                    "SetHoldType": HoldType.STANDBY
                    if preset == PRESET_OFF
                    else HoldType.ECO
                    if preset == PRESET_ECO
                    else HoldType.PERMANENT_HOLD
                    if preset == PRESET_PERMANENT_HOLD
                    else HoldType.TEMPORARY_HOLD
                    if preset == PRESET_TEMPORARY_HOLD
                    else HoldType.FOLLOW_SCHEDULE
                }
            }
        else:
            request_data = {
                "sIT600TH": {
                    "SetHoldType": HoldType.STANDBY
                    if preset == PRESET_OFF
                    else HoldType.PERMANENT_HOLD
                    if preset == PRESET_PERMANENT_HOLD
                    else HoldType.FOLLOW_SCHEDULE
                }
            }

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
        """Set a climate HVAC mode supported by the target device."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        mode = _validate_supported_value(mode, "mode", device.hvac_modes)
        request_data: dict[str, dict[str, int]]

        if device.model == MODEL_FC600:
            request_data = {
                "sTherS": {
                    "SetSystemMode": SystemMode.HEAT
                    if mode == HVAC_MODE_HEAT
                    else SystemMode.COOL
                    if mode == HVAC_MODE_COOL
                    else SystemMode.AUTO
                }
            }
        else:
            request_data = {
                "sIT600TH": {
                    "SetHoldType": HoldType.STANDBY
                    if mode == HVAC_MODE_OFF
                    else HoldType.FOLLOW_SCHEDULE
                }
            }

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
        """Set an FC600 fan mode supported by the target device."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        if device.fan_modes is None:
            raise ValueError(f"climate device {device_id!r} does not support fan modes")
        mode = _validate_supported_value(mode, "mode", device.fan_modes)

        request_data: dict[str, dict[str, int]] = {
            "sFanS": {
                "FanMode": FanMode.AUTO
                if mode == FAN_MODE_AUTO
                else FanMode.HIGH
                if mode == FAN_MODE_HIGH
                else FanMode.MEDIUM
                if mode == FAN_MODE_MEDIUM
                else FanMode.LOW
                if mode == FAN_MODE_LOW
                else FanMode.OFF
            }
        }

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
        """Enable or disable the FC600 keypad lock."""

        if not isinstance(locked, bool):
            raise TypeError("locked must be a bool")

        device = self._require_device(device_id, self._climate_devices, "climate")
        request_data: dict[str, dict[str, int]] = {
            "sTherUIS": {"LockKey": 1 if locked else 0}
        }

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

    async def set_climate_device_temperature(
        self, device_id: str, setpoint_celsius: float
    ) -> None:
        """Set a climate target temperature in Celsius."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        setpoint_celsius = _validate_setpoint(
            setpoint_celsius,
            device.min_temp,
            device.max_temp,
        )
        rounded_setpoint = int(self.round_to_half(setpoint_celsius) * TEMPERATURE_SCALE)
        request_data: dict[str, dict[str, int]]

        if device.model == MODEL_FC600:
            if device.hvac_mode == HVAC_MODE_COOL:
                request_data = {"sTherS": {"SetCoolingSetpoint_x100": rounded_setpoint}}
            else:
                request_data = {"sTherS": {"SetHeatingSetpoint_x100": rounded_setpoint}}
        else:
            request_data = {"sIT600TH": {"SetHeatingSetpoint_x100": rounded_setpoint}}

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
        """Round a number to the nearest half step."""

        return round(number * 2) / 2

    async def add_climate_update_callback(self, method: UpdateCallback) -> None:
        """Register an async callback called after climate device refreshes."""

        self._climate_update_callbacks.append(_validate_callback(method))

    async def add_binary_sensor_update_callback(self, method: UpdateCallback) -> None:
        """Register an async callback called after binary sensor refreshes."""

        self._binary_sensor_update_callbacks.append(_validate_callback(method))

    async def add_switch_update_callback(self, method: UpdateCallback) -> None:
        """Register an async callback called after switch refreshes."""

        self._switch_update_callbacks.append(_validate_callback(method))

    async def add_cover_update_callback(self, method: UpdateCallback) -> None:
        """Register an async callback called after cover refreshes."""

        self._cover_update_callbacks.append(_validate_callback(method))

    async def add_sensor_update_callback(self, method: UpdateCallback) -> None:
        """Register an async callback called after sensor refreshes."""

        self._sensor_update_callbacks.append(_validate_callback(method))

    async def _make_encrypted_request(
        self,
        command: str,
        request_body: dict[str, Any],
    ) -> dict[str, Any]:
        """Makes encrypted Salus iT600 json request, decrypts and returns response."""

        async with self._lock:
            if self._session is None:
                self._session = aiohttp.ClientSession()
                self._close_session = True

            try:
                request_url = f"http://{self._host}:{self._port}/deviceid/{command}"
                request_body_json = json.dumps(request_body)

                if self._debug:
                    _LOGGER.debug(
                        "Gateway request: POST %s\n%s\n", request_url, request_body_json
                    )

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
                _LOGGER.exception(
                    "Unexpected error while communicating with iT600 gateway"
                )
                raise

    async def close(self) -> None:
        """Close the internally owned aiohttp session, if one was created."""

        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "IT600Gateway":
        """Return this gateway for use as an async context manager."""

        return self

    async def __aexit__(self, *exc_info: object) -> None:
        """Close internally owned resources on async context-manager exit."""

        await self.close()
