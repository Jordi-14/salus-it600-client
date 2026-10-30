"""Salus iT600 gateway API."""

import asyncio
import json
import logging
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Self, TypeVar

import aiohttp
from aiohttp import client_exceptions

from .comfort_warm_floor import (
    NON_SETTINGS_RESPONSE,
    build_comfort_warm_floor_command,
    comfort_command_matches,
    comfort_command_response,
    validated_comfort_settings,
)
from .const import (
    COVER_POSITION_MAX,
    COVER_POSITION_MIN,
    FAN_MODE_AUTO,
    FAN_MODE_HIGH,
    FAN_MODE_LOW,
    FAN_MODE_MEDIUM,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_ECO,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
    PRESET_SCHEDULE_OVERRIDE,
    TEMPERATURE_SCALE,
    FanMode,
    HoldType,
    SystemMode,
)
from .device_models import (
    is_binary_sensor_summary,
    is_fan_coil_model,
    is_sq610_model,
    is_trv_model,
)
from .encryptor import IT600Encryptor
from .exceptions import (
    IT600AuthenticationError,
    IT600CommandError,
    IT600ConnectionError,
    IT600DeviceNotFoundError,
    IT600UnsupportedFirmwareError,
    IT600ValidationError,
)
from .models import (
    BinarySensorDevice,
    ClimateDevice,
    CoverDevice,
    GatewayDevice,
    SensorDevice,
    SwitchDevice,
    active_climate_system_mode,
    active_temperature_range,
)
from .parsers import (
    PARSING_EXCEPTIONS,
    parse_binary_diagnostic_devices,
    parse_binary_sensor_device,
    parse_climate_binary_sensor_devices,
    parse_climate_device,
    parse_climate_sensor_devices,
    parse_cover_device,
    parse_meter_sensor_devices,
    parse_sensor_devices,
    parse_switch_device,
    parse_switch_sensor_devices,
    parse_wiring_centre_binary_sensor_devices,
    parse_wiring_centre_device,
    parse_wiring_centre_sensor_devices,
)
from .protocol import (
    GatewayProtocol,
    ProtocolDetectionError,
    ProtocolRejected,
    ProtocolUnsupported,
    parse_frame_33,
)
from .protocol_aes_cbc import AesCbcProtocol
from .protocol_aes_ccm import AesCcmProtocol

_LOGGER = logging.getLogger("salus_it600")

DEVICE_NOT_FOUND_ERROR = "{device_type} device not found with id: {device_id}"
_SQ610_WRITE_HEATING_SETPOINT = "SetHeatingSetpoint_x100"
_SQ610_WRITE_COOLING_SETPOINT = "SetCoolingSetpoint_x100"
_SQ610_WRITE_HOLD_TYPE = "SetHoldType"
_SQ610_WRITE_SYSTEM_MODE = "SetSystemMode"
_SQ610_WRITE_LOCK_KEY = "SetLockKey"
# The gateway drops idle keep-alive connections without telling the client, so
# the next request on a reused connection fails with ServerDisconnectedError.
# One retry opens a fresh connection for ordinary requests. Sequenced settings
# commands explicitly disable replay because their outcome can be uncertain.
_DISCONNECT_RETRY_ATTEMPTS = 2
_DISCONNECT_RETRY_DELAY = 0.2
# Consecutive connection failures on the combined detail request before the
# client stops trying it and keeps using one request per device family.
_COMBINED_DETAIL_FAILURE_LIMIT = 3
_FAN_COIL_PRESET_HOLD_TYPES = {
    PRESET_OFF: HoldType.STANDBY,
    PRESET_ECO: HoldType.ECO,
    PRESET_PERMANENT_HOLD: HoldType.PERMANENT_HOLD,
}
_HEAT_ONLY_PRESET_HOLD_TYPES = {
    PRESET_OFF: HoldType.STANDBY,
    PRESET_AWAY: HoldType.AWAY,
    PRESET_PERMANENT_HOLD: HoldType.PERMANENT_HOLD,
}
_SQ610_PRESET_HOLD_TYPES = {
    PRESET_OFF: HoldType.STANDBY,
    PRESET_AWAY: HoldType.AWAY,
    PRESET_PERMANENT_HOLD: HoldType.PERMANENT_HOLD,
}
_FAN_COIL_HVAC_MODES = {
    HVAC_MODE_HEAT: SystemMode.HEAT,
    HVAC_MODE_COOL: SystemMode.COOL,
}
_SQ610_HVAC_MODES = {
    HVAC_MODE_HEAT: SystemMode.HEAT,
    HVAC_MODE_COOL: SystemMode.COOL,
}
_HEAT_ONLY_HVAC_HOLD_TYPES = {
    HVAC_MODE_OFF: HoldType.STANDBY,
    HVAC_MODE_HEAT: HoldType.PERMANENT_HOLD,
}
_FAN_MODES = {
    FAN_MODE_AUTO: FanMode.AUTO,
    FAN_MODE_HIGH: FanMode.HIGH,
    FAN_MODE_MEDIUM: FanMode.MEDIUM,
    FAN_MODE_LOW: FanMode.LOW,
}
DeviceT = TypeVar(
    "DeviceT",
    ClimateDevice,
    BinarySensorDevice,
    SwitchDevice,
    CoverDevice,
    SensorDevice,
)


def _validate_non_empty_string(value: str, field_name: str) -> str:
    """Validate a public string argument and return its stripped value."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()
    if not normalized:
        raise IT600ValidationError(f"{field_name} must not be empty")

    return normalized


def _validate_positive_number(value: float, field_name: str) -> int | float:
    """Validate a positive numeric argument."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")
    if value <= 0:
        raise IT600ValidationError(f"{field_name} must be greater than 0")
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
        raise IT600ValidationError(
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
        raise IT600ValidationError(
            f"{field_name} must be one of {sorted(supported_values)}, got "
            f"{normalized!r}"
        )
    return normalized


def _validate_setpoint(
    value: float,
    min_temp: float,
    max_temp: float,
) -> float:
    """Validate a temperature setpoint against the device-supported range."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("setpoint_celsius must be a number")

    setpoint = float(value)
    if setpoint < min_temp or setpoint > max_temp:
        raise IT600ValidationError(f"setpoint_celsius must be between {min_temp} and {max_temp}")
    return setpoint


def _uses_cooling_setpoint(device: ClimateDevice) -> bool:
    """Return whether writes should target the cooling setpoint."""
    return active_climate_system_mode(
        system_mode=device.system_mode,
        hvac_mode=device.hvac_mode,
        running_state=device.running_state,
    ) == int(SystemMode.COOL)


def _active_temperature_write_range(device: ClimateDevice) -> tuple[float, float]:
    """Return the active heat/cool setpoint bounds with device min/max fallback."""
    min_temp, max_temp = active_temperature_range(
        system_mode=device.system_mode,
        min_heat_temp=device.min_heat_temp,
        max_heat_temp=device.max_heat_temp,
        min_cool_temp=device.min_cool_temp,
        max_cool_temp=device.max_cool_temp,
        hvac_mode=device.hvac_mode,
        running_state=device.running_state,
    )
    return (
        device.min_temp if min_temp is None else min_temp,
        device.max_temp if max_temp is None else max_temp,
    )


def _gateway_mac_from_readall(response: dict[str, Any]) -> str | None:
    """Return gateway MAC from a readall response, if present."""
    devices = response.get("id", [])
    if not isinstance(devices, list):
        return None

    for device in devices:
        if not isinstance(device, dict):
            continue
        gateway_mac = device.get("sGateway", {}).get("NetworkLANMAC")
        if isinstance(gateway_mac, str) and gateway_mac:
            return gateway_mac
    return None


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


def _validate_http_status(status: int, context: str) -> None:
    """Raise a typed exception for non-successful gateway HTTP responses."""
    if status == 200:
        return

    raise IT600ConnectionError(
        f"Gateway {context} request failed with HTTP status {status}"
    )


def _raise_for_gateway_frame(raw: bytes, context: str) -> None:
    """Raise a typed exception for known fixed-length gateway protocol frames."""
    frame = parse_frame_33(raw)
    if frame is None:
        return

    raise IT600UnsupportedFirmwareError(
        f"Gateway returned a {frame.trailer_name} frame during {context} request"
    )


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


DetailIndex = dict[Any, list[dict[str, Any]]]


def _detail_items_by_device(items: list[dict[str, Any]]) -> DetailIndex:
    """Group detail payloads by UniID, keeping one per (UniID, Endpoint)."""
    grouped: DetailIndex = {}
    seen: set[tuple[Any, Any]] = set()
    for item in items:
        data = item.get("data")
        if not isinstance(data, dict):
            continue
        key = (data.get("UniID"), data.get("Endpoint"))
        if key in seen:
            continue
        seen.add(key)
        grouped.setdefault(key[0], []).append(item)
    return grouped


def _find_detail_items(
    grouped: Mapping[Any, list[dict[str, Any]]],
    request_data: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Return the detail payloads that answer one deviceid request item.

    Discovery summaries do not always carry an Endpoint while detail payloads
    do. Without an Endpoint the gateway answers with every endpoint of the
    device (for example both channels of a two-channel switch), so all of them
    are returned. With an Endpoint only that endpoint matches.
    """
    items = grouped.get(request_data.get("UniID"), [])
    if "Endpoint" not in request_data:
        return list(items)
    endpoint = request_data["Endpoint"]
    return [item for item in items if item["data"].get("Endpoint") == endpoint]


def _select_detail_items(
    grouped: Mapping[Any, list[dict[str, Any]]],
    request_items: list[dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Return the detail payloads for a family, each payload at most once.

    Overlapping discovery entries (one with and one without an Endpoint) match
    the same payload, which must not be parsed twice.
    """
    selected: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any]] = set()
    for request_item in request_items:
        for item in _find_detail_items(grouped, request_item["data"]):
            key = (item["data"].get("UniID"), item["data"].get("Endpoint"))
            if key not in seen:
                seen.add(key)
                selected.append(item)
    return selected


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
        request_timeout: float = 5,
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

        self._euid = euid
        self._encryptor = IT600Encryptor(euid)
        self._protocol: GatewayProtocol | None = None
        self._host = host
        self._port = port
        self._request_timeout = request_timeout
        self._disconnect_retry_delay = _DISCONNECT_RETRY_DELAY
        self._debug = debug
        self._lock = asyncio.Lock()  # Gateway supports very few concurrent requests
        self._comfort_floor_lock = asyncio.Lock()
        self._pending_floor_commands: dict[str, tuple[str, float]] = {}

        self._session = session
        self._close_session = False

        self._gateway_device: GatewayDevice | None = None

        self._climate_devices: dict[str, ClimateDevice] = {}

        self._binary_sensor_devices: dict[str, BinarySensorDevice] = {}
        self._climate_binary_sensor_devices: dict[str, BinarySensorDevice] = {}
        self._binary_sensor_diagnostic_devices: dict[str, BinarySensorDevice] = {}
        self._wiring_centre_binary_sensor_devices: dict[str, BinarySensorDevice] = {}

        self._switch_devices: dict[str, SwitchDevice] = {}

        self._cover_devices: dict[str, CoverDevice] = {}

        self._sensor_devices: dict[str, SensorDevice] = {}
        # Devices whose parse failure was already logged with a traceback.
        self._logged_parse_failures: set[tuple[str, str]] = set()
        # Detail payloads fetched for the whole poll in one deviceid request.
        self._prefetched_details: DetailIndex | None = None
        self._combined_detail_requests = True
        self._combined_detail_failures = 0
        self._climate_sensor_devices: dict[str, SensorDevice] = {}
        self._switch_sensor_devices: dict[str, SensorDevice] = {}
        self._meter_sensor_devices: dict[str, SensorDevice] = {}
        self._wiring_centre_sensor_devices: dict[str, SensorDevice] = {}

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

        if self._protocol is None:
            return await self._connect_with_protocol_detection()

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
                await self._probe_gateway_root()
            except (TimeoutError, client_exceptions.ClientError):
                raise IT600ConnectionError(
                    "Error occurred while communicating with iT600 gateway: "
                    "check if you have specified host/IP address correctly"
                ) from ae

            raise IT600AuthenticationError(
                "Error occurred while communicating with iT600 gateway: "
                "check if you have specified EUID correctly"
            ) from ae

    def _log_parse_failure(
        self,
        device_type: str,
        unique_id: Any,
        err: Exception,
    ) -> None:
        """Log a device parse failure.

        A malformed device fails on every poll, so the traceback is logged once
        per device and later failures go to debug level.
        """
        key = (device_type, str(unique_id))
        if key in self._logged_parse_failures:
            _LOGGER.debug(
                "Failed to parse %s device %s: %r", device_type, unique_id, err
            )
            return
        self._logged_parse_failures.add(key)
        _LOGGER.error(
            "Failed to parse %s device %s; repeats are logged at debug level",
            device_type,
            unique_id,
            exc_info=err,
        )

    def _protocol_candidates(self) -> list[GatewayProtocol]:
        """Return protocol candidates in the order they should be attempted."""
        candidates: list[GatewayProtocol] = [
            AesCbcProtocol(self._euid),
            AesCbcProtocol(self._euid, aes128=True),
        ]
        try:
            candidates.append(AesCcmProtocol(self._euid))
        except ValueError:
            _LOGGER.debug("Skipping AES-CCM candidate because EUID is not hex")
        return candidates

    async def _connect_with_protocol_detection(self) -> str:
        """Detect the gateway encryption protocol and return the gateway MAC."""
        assert self._session is not None
        result: dict[str, Any] | None = None
        saw_reject = False
        saw_unsupported_protocol = False

        for protocol in self._protocol_candidates():
            try:
                _LOGGER.debug("Trying Salus protocol: %s", protocol.name)
                result = await protocol.connect(
                    self._session,
                    self._host,
                    self._port,
                    self._request_timeout,
                )
                self._protocol = protocol
                _LOGGER.debug("Salus protocol %s succeeded", protocol.name)
                break
            except (ProtocolRejected, ProtocolUnsupported) as exc:
                _LOGGER.debug("Salus protocol %s failed: %s", protocol.name, exc)
                if isinstance(exc, ProtocolRejected):
                    saw_reject = True
                else:
                    saw_unsupported_protocol = True
            except ProtocolDetectionError as exc:
                _LOGGER.debug("Salus protocol %s failed: %s", protocol.name, exc)
            except Exception as exc:  # noqa: BLE001 - keep probing the next protocol
                # Protocol detection is a probe: any failure means "not this
                # protocol", including ones the protocol implementations do not
                # wrap. A hard error is raised below only once every candidate
                # has been tried.
                _LOGGER.debug("Salus protocol %s failed: %s", protocol.name, exc)

        if result is not None:
            gateway_mac = _gateway_mac_from_readall(result)
            if gateway_mac is not None:
                return gateway_mac
            raise IT600CommandError(
                "Error occurred while communicating with iT600 gateway: "
                "response did not contain gateway information"
            )

        try:
            await self._probe_gateway_root()
        except (TimeoutError, client_exceptions.ClientError) as exc:
            raise IT600ConnectionError(
                "Error occurred while communicating with iT600 gateway: "
                "check if you have specified host/IP address correctly"
            ) from exc

        if saw_reject or saw_unsupported_protocol:
            raise IT600UnsupportedFirmwareError(
                "Gateway is reachable but uses an unsupported encryption protocol"
            )

        raise IT600AuthenticationError(
            "Error occurred while communicating with iT600 gateway: "
            "check if you have specified EUID correctly"
        )

    def _client_timeout(self) -> aiohttp.ClientTimeout:
        """Return the per-request timeout used for gateway HTTP calls."""
        return aiohttp.ClientTimeout(total=self._request_timeout)

    async def _probe_gateway_root(self) -> None:
        """Probe the gateway root endpoint with normal response cleanup."""
        if self._session is None:
            raise IT600ConnectionError("Gateway session has not been initialized")

        async with self._session.get(
            f"http://{self._host}:{self._port}/",
            timeout=self._client_timeout(),
        ) as resp:
            await resp.read()

    @property
    def combined_detail_requests(self) -> bool:
        """Return whether polls fetch all device details in one request.

        Starts True and switches to False for the rest of this client's life
        if the gateway rejects the combined request, leaves devices out of the
        answer, or drops it repeatedly.
        """
        return self._combined_detail_requests

    async def poll_status(self) -> None:
        """Refresh all known device collections from the gateway.

        The method performs a `readall` discovery request, then fetches the
        detailed status of every device. It asks for all devices in one
        `deviceid` request and falls back to one request per device family when
        the gateway does not handle that. Invalid individual devices are logged
        and skipped; gateway communication errors propagate to the caller.
        """

        all_devices = await self._make_encrypted_request(
            "read", {"requestAttr": "readall"}
        )

        device_items = _response_items(all_devices, "readall")

        gateway_devices = list(filter(lambda x: "sGateway" in x, device_items))
        climate_devices = list(
            filter(lambda x: ("sIT600TH" in x) or ("sTherS" in x), device_items)
        )
        wiring_centres = list(filter(lambda x: "sIT600WC" in x, device_items))
        binary_sensors = list(filter(is_binary_sensor_summary, device_items))
        sensors = list(filter(lambda x: "sTempS" in x, device_items))
        switches = list(filter(lambda x: "sOnOffS" in x, device_items))
        covers = list(filter(lambda x: "sLevelS" in x, device_items))
        meters = list(
            filter(
                lambda x: "sMeterS" in x and "sOnOffS" not in x,
                device_items,
            )
        )
        families = [
            gateway_devices,
            climate_devices,
            wiring_centres,
            binary_sensors,
            sensors,
            switches,
            covers,
            meters,
        ]

        self._prefetched_details = await self._prefetch_device_details(families)
        try:
            await self._refresh_gateway_device(gateway_devices)
            await self._refresh_climate_devices(climate_devices)
            await self._refresh_wiring_centre_devices(wiring_centres)
            await self._refresh_binary_sensor_devices(binary_sensors)
            await self._refresh_sensor_devices(sensors)
            await self._refresh_switch_devices(switches)
            await self._refresh_cover_devices(covers)
            await self._refresh_meter_devices(meters)
        finally:
            self._prefetched_details = None

    async def _prefetch_device_details(
        self,
        families: list[list[Any]],
    ) -> DetailIndex | None:
        """Fetch every device's detail payload in one deviceid request.

        Returns None, so each family is requested separately, when combined
        requests are disabled, when there is nothing to gain, or when the
        combined request fails. A rejected or incomplete answer disables the
        combined request for good; dropped connections disable it after a few
        consecutive failures.
        """
        if not self._combined_detail_requests:
            return None
        if sum(1 for family in families if family) < 2:
            return None

        request_items: list[dict[str, dict[str, Any]]] = []
        seen: set[tuple[Any, Any]] = set()
        for family in families:
            for device in family:
                data = device.get("data") if isinstance(device, dict) else None
                if not isinstance(data, dict):
                    continue
                key = (data.get("UniID"), data.get("Endpoint"))
                if key in seen:
                    continue
                seen.add(key)
                request_items.append({"data": data})
        if not request_items:
            return None

        try:
            response = await self._make_encrypted_request(
                "read",
                {"requestAttr": "deviceid", "id": request_items},
            )
            items = _response_items(response, "combined device detail")
        except IT600CommandError as err:
            self._disable_combined_detail_requests(f"gateway rejected it: {err}")
            return None
        except IT600ConnectionError as err:
            self._combined_detail_failures += 1
            _LOGGER.debug(
                "Combined device detail request failed (%s/%s): %s",
                self._combined_detail_failures,
                _COMBINED_DETAIL_FAILURE_LIMIT,
                err,
            )
            if self._combined_detail_failures >= _COMBINED_DETAIL_FAILURE_LIMIT:
                self._disable_combined_detail_requests("repeated connection failures")
            return None

        indexed = _detail_items_by_device(items)
        missing = [
            item["data"].get("UniID")
            for item in request_items
            if not _find_detail_items(indexed, item["data"])
        ]
        if missing:
            self._disable_combined_detail_requests(
                f"answer left out {len(missing)} of {len(request_items)} devices"
            )
            return None

        self._combined_detail_failures = 0
        return indexed

    def _disable_combined_detail_requests(self, reason: str) -> None:
        """Switch to one deviceid request per device family."""
        self._combined_detail_requests = False
        _LOGGER.info(
            "Requesting Salus device details per device family from now on "
            "because the combined request did not work (%s)",
            reason,
        )

    async def _refresh_device_collection(
        self,
        devices: list[Any],
        device_type: str,
        state_attr: str,
        parser: Callable[[dict[str, Any]], Any | None],
    ) -> None:
        """Refresh one device collection using a parser for that device type."""
        local_devices: dict[str, Any] = {}

        for device_status in await self._device_detail_statuses(devices, device_type):
            unique_id = device_status.get("data", {}).get("UniID")
            try:
                device = parser(device_status)
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure(device_type, unique_id, err)
                continue

            if device is None:
                continue

            local_devices[device.unique_id] = device

        setattr(self, state_attr, local_devices)
        _LOGGER.debug(
            "Refreshed %s %s devices",
            len(local_devices),
            device_type,
        )

    async def _device_detail_statuses(
        self,
        devices: list[Any],
        device_type: str,
    ) -> list[dict[str, Any]]:
        """Fetch detailed status payloads for one device family."""
        if not devices:
            return []

        request_items = _device_status_request_items(devices, device_type)
        if not request_items:
            return []

        prefetched = self._prefetched_details
        if prefetched is not None:
            return _select_detail_items(prefetched, request_items)

        status = await self._make_encrypted_request(
            "read",
            {"requestAttr": "deviceid", "id": request_items},
        )
        return _response_items(status, f"{device_type} device detail")

    async def _refresh_gateway_device(
        self,
        devices: list[Any],
    ) -> None:
        local_device: GatewayDevice | None = None

        for device_status in await self._device_detail_statuses(devices, "gateway"):
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
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure("gateway", unique_id, err)

        self._gateway_device = local_device
        _LOGGER.debug("Refreshed gateway device")

    async def _refresh_cover_devices(
        self,
        devices: list[Any],
    ) -> None:
        await self._refresh_device_collection(
            devices,
            "cover",
            "_cover_devices",
            parse_cover_device,
        )

    async def _refresh_switch_devices(
        self,
        devices: list[Any],
    ) -> None:
        local_devices: dict[str, SwitchDevice] = {}
        sensor_devices: dict[str, SensorDevice] = {}

        for device_status in await self._device_detail_statuses(devices, "switch"):
            unique_id = device_status.get("data", {}).get("UniID")
            try:
                device = parse_switch_device(device_status)
                sensors = parse_switch_sensor_devices(device_status)
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure("switch", unique_id, err)
                continue

            if device is not None:
                local_devices[device.unique_id] = device

            for sensor in sensors:
                sensor_devices[sensor.unique_id] = sensor

        self._switch_devices = local_devices
        self._switch_sensor_devices = sensor_devices
        _LOGGER.debug("Refreshed %s switch devices", len(local_devices))

    async def _refresh_sensor_devices(
        self,
        devices: list[Any],
    ) -> None:
        local_devices: dict[str, SensorDevice] = {}

        for device_status in await self._device_detail_statuses(devices, "sensor"):
            unique_id = device_status.get("data", {}).get("UniID")
            try:
                sensors = parse_sensor_devices(device_status)
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure("sensor", unique_id, err)
                continue

            for sensor in sensors:
                local_devices[sensor.unique_id] = sensor

        self._sensor_devices = local_devices
        _LOGGER.debug("Refreshed %s sensor devices", len(local_devices))

    async def _refresh_meter_devices(
        self,
        devices: list[Any],
    ) -> None:
        sensor_devices: dict[str, SensorDevice] = {}

        for device_status in await self._device_detail_statuses(devices, "meter"):
            unique_id = device_status.get("data", {}).get("UniID")
            try:
                sensors = parse_meter_sensor_devices(device_status)
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure("meter", unique_id, err)
                continue

            for sensor in sensors:
                sensor_devices[sensor.unique_id] = sensor

        self._meter_sensor_devices = sensor_devices
        _LOGGER.debug("Refreshed %s meter sensor devices", len(sensor_devices))

    async def _refresh_binary_sensor_devices(
        self,
        devices: list[Any],
    ) -> None:
        local_devices: dict[str, BinarySensorDevice] = {}
        diagnostic_devices: dict[str, BinarySensorDevice] = {}

        for device_status in await self._device_detail_statuses(
            devices,
            "binary sensor",
        ):
            unique_id = device_status.get("data", {}).get("UniID")
            try:
                device = parse_binary_sensor_device(device_status)
                diagnostics = parse_binary_diagnostic_devices(device_status)
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure("binary sensor", unique_id, err)
                continue

            if device is not None:
                local_devices[device.unique_id] = device

            for diagnostic in diagnostics:
                diagnostic_devices[diagnostic.unique_id] = diagnostic

        self._binary_sensor_devices = local_devices
        self._binary_sensor_diagnostic_devices = diagnostic_devices
        _LOGGER.debug("Refreshed %s binary sensor devices", len(local_devices))

    async def _refresh_climate_devices(
        self,
        devices: list[Any],
    ) -> None:
        local_devices: dict[str, ClimateDevice] = {}
        sensor_devices: dict[str, SensorDevice] = {}
        binary_devices: dict[str, BinarySensorDevice] = {}

        # Signal-quality readings are absent from most polls even for healthy
        # devices, so the previous collection is handed to the parser to carry
        # the last known value forward.
        previous_sensors = self._climate_sensor_devices

        for device_status in await self._device_detail_statuses(devices, "climate"):
            unique_id = device_status.get("data", {}).get("UniID")
            try:
                device = parse_climate_device(device_status)
                if device is None:
                    continue
                sensors = parse_climate_sensor_devices(
                    device_status,
                    device,
                    previous_sensors,
                )
                binary_sensors = parse_climate_binary_sensor_devices(
                    device_status,
                    device,
                )
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure("climate", unique_id, err)
                continue

            local_devices[device.unique_id] = device

            for sensor in sensors:
                sensor_devices[sensor.unique_id] = sensor

            for binary_sensor in binary_sensors:
                binary_devices[binary_sensor.unique_id] = binary_sensor

        self._climate_devices = local_devices
        self._climate_sensor_devices = sensor_devices
        self._climate_binary_sensor_devices = binary_devices
        _LOGGER.debug("Refreshed %s climate devices", len(local_devices))

    async def _refresh_wiring_centre_devices(
        self,
        devices: list[Any],
    ) -> None:
        binary_devices: dict[str, BinarySensorDevice] = {}
        sensor_devices: dict[str, SensorDevice] = {}

        # Signal-quality readings are absent from most polls even for healthy
        # devices, so the previous collection is handed to the parser to carry
        # the last known value forward.
        previous_sensors = self._wiring_centre_sensor_devices

        for device_status in await self._device_detail_statuses(
            devices,
            "wiring centre",
        ):
            unique_id = device_status.get("data", {}).get("UniID")
            try:
                connectivity = parse_wiring_centre_device(device_status)
                problem_sensors = parse_wiring_centre_binary_sensor_devices(
                    device_status,
                )
                signal_sensors = parse_wiring_centre_sensor_devices(
                    device_status,
                    previous_sensors,
                )
            except PARSING_EXCEPTIONS as err:
                self._log_parse_failure("wiring centre", unique_id, err)
                continue

            if connectivity is not None:
                binary_devices[connectivity.unique_id] = connectivity

            for problem_sensor in problem_sensors:
                binary_devices[problem_sensor.unique_id] = problem_sensor

            for signal_sensor in signal_sensors:
                sensor_devices[signal_sensor.unique_id] = signal_sensor

        self._wiring_centre_binary_sensor_devices = binary_devices
        self._wiring_centre_sensor_devices = sensor_devices
        _LOGGER.debug("Refreshed %s wiring centre devices", len(binary_devices))

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
            raise IT600DeviceNotFoundError(
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

        return {
            **self._binary_sensor_devices,
            **self._climate_binary_sensor_devices,
            **self._binary_sensor_diagnostic_devices,
            **self._wiring_centre_binary_sensor_devices,
        }

    def get_binary_sensor_device(self, device_id: str) -> BinarySensorDevice | None:
        """Return one cached binary sensor device, or None if it is not loaded."""

        device_id = self._validate_device_id(device_id)
        return (
            self._binary_sensor_devices.get(device_id)
            or self._climate_binary_sensor_devices.get(device_id)
            or self._binary_sensor_diagnostic_devices.get(device_id)
            or self._wiring_centre_binary_sensor_devices.get(device_id)
        )

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

        return {
            **self._sensor_devices,
            **self._climate_sensor_devices,
            **self._switch_sensor_devices,
            **self._meter_sensor_devices,
            **self._wiring_centre_sensor_devices,
        }

    def get_sensor_device(self, device_id: str) -> SensorDevice | None:
        """Return one cached sensor device, or None if it is not loaded."""

        device_id = self._validate_device_id(device_id)
        return (
            self._sensor_devices.get(device_id)
            or self._climate_sensor_devices.get(device_id)
            or self._switch_sensor_devices.get(device_id)
            or self._meter_sensor_devices.get(device_id)
            or self._wiring_centre_sensor_devices.get(device_id)
        )

    async def fetch_sq610_properties(
        self,
        device_ids: Sequence[str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Fetch flattened raw gateway properties for cached SQ610 devices.

        Args:
            device_ids: Optional SQ610 climate device IDs. When omitted, all
                cached SQ610 climate devices are fetched.

        Raises:
            IT600DeviceNotFoundError: If a requested device is not in the
                climate cache.
            IT600ValidationError: If a requested device is not an SQ610 model.
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
                    raise IT600ValidationError(f"climate device {device_id!r} is not an SQ610")
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

    def _comfort_floor_time(self) -> float:
        return asyncio.get_running_loop().time()

    async def _read_comfort_status(self, device: ClimateDevice) -> dict[str, Any]:
        """Read one fresh matching online device; never replay a settings write."""
        response = await self._make_encrypted_request(
            "read", {"requestAttr": "deviceid", "id": [{"data": device.data}]},
        )
        matches = [item for item in _response_items(response, "floor-comfort detail")
                   if item.get("data") == device.data and item.get("status") == "success"]
        if len(matches) != 1:
            raise IT600CommandError("Expected one successful floor-comfort device response")
        status = matches[0]
        if status.get("sZDOInfo", {}).get("OnlineStatus_i") != 1:
            raise IT600ValidationError("Cannot change floor comfort on an offline device")
        validated_comfort_settings(status, check_command=False)
        return status

    async def set_climate_device_comfort_warm_floor(self, device_id: str, level: int) -> None:
        """Send one profile-gated settings write; return on gateway acknowledgement.

        Acknowledgement is not device confirmation. Poll normally to observe the
        device. The local pending guard expires after 120 seconds; it never
        replays a command or restores a stale snapshot. Schedule-driven runtime
        fields and replacement app echoes do not prevent resolution.
        """
        level = _validate_int_range(level, "comfort warm floor level", 0, 3)
        device = self._require_device(device_id, self._climate_devices, "climate")
        if not device.available:
            raise IT600ValidationError("Cannot change floor comfort on an offline device")
        async with self._comfort_floor_lock:
            status = await self._read_comfort_status(device)
            pending = self._pending_floor_commands.get(device_id)
            expired_command = None
            if pending is not None:
                previous_command, expires_at = pending
                if comfort_command_matches(status, previous_command):
                    del self._pending_floor_commands[device_id]
                elif self._comfort_floor_time() < expires_at:
                    raise IT600ValidationError("Previous floor-comfort command is still pending or uncertain")
                else:
                    del self._pending_floor_commands[device_id]
                    expired_command = previous_command
            echo = comfort_command_response(status)
            # Only a known, expired local echo may bypass the in-flight echo
            # check. Unknown external commands still use the strict guard.
            stale_local_echo = expired_command is not None and echo == expired_command.lower() + "00"
            original = validated_comfort_settings(status, check_command=not stale_local_echo)
            if stale_local_echo or echo == NON_SETTINGS_RESPONSE:
                await asyncio.sleep(2)
                stable = await self._read_comfort_status(device)
                if validated_comfort_settings(stable, check_command=False) != original:
                    raise IT600ValidationError("Floor-comfort settings changed during stability check")
                if comfort_command_response(stable) != comfort_command_response(status):
                    stale_local_echo = False
                    validated_comfort_settings(stable)
                status = stable
            command = build_comfort_warm_floor_command(status, level, check_command=not stale_local_echo)
            if command is None:
                return
            self._pending_floor_commands[device_id] = (command, self._comfort_floor_time() + 120)
            result = await self._make_encrypted_request(
                "write", {"requestAttr": "write", "id": [
                    {"data": device.data, "sIT600I": {"SetCommand_d": command}},
                ]}, retry_disconnect=False,
            )
            items = _response_items(result, "floor-comfort write")
            if (len(items) != 1 or items[0].get("status") != "success"
                    or items[0].get("data", {}).get("UniID") != device.unique_id
                    or items[0].get("data", {}).get("Endpoint") != device.data.get("Endpoint")):
                raise IT600CommandError("Gateway did not acknowledge the floor-comfort write")

    async def _write_sq610_property(
        self,
        device: ClimateDevice,
        prop: str,
        value: int,
    ) -> None:
        """Write one validated SQ610 `sIT600TH` property for a cached device."""
        await self._write_device(device, {"sIT600TH": {prop: int(value)}})

    async def _write_device(
        self,
        device: Any,
        request_data: dict[str, dict[str, Any]],
    ) -> None:
        """Write one encrypted command envelope for a cached device."""
        await self._make_encrypted_request(
            "write",
            {
                "requestAttr": "write",
                "id": [{"data": device.data, **request_data}],
            },
        )

    async def _set_switch_device_state(self, device_id: str, is_on: bool) -> None:
        """Set a switch or relay device state."""
        device = self._require_device(device_id, self._switch_devices, "switch")
        await self._write_device(device, {"sOnOffS": {"SetOnOff": int(is_on)}})

    async def set_cover_position(self, device_id: str, position: int) -> None:
        """Move a cover to a position where 0 is closed and 100 is open."""

        position = _validate_int_range(
            position,
            "position",
            COVER_POSITION_MIN,
            COVER_POSITION_MAX,
        )
        device = self._require_device(device_id, self._cover_devices, "cover")

        await self._write_device(
            device,
            {"sLevelS": {"SetMoveToLevel": f"{format(position, '02x')}FFFF"}},
        )

    async def open_cover(self, device_id: str) -> None:
        """Open a cover fully."""

        await self.set_cover_position(device_id, COVER_POSITION_MAX)

    async def close_cover(self, device_id: str) -> None:
        """Close a cover fully."""

        await self.set_cover_position(device_id, COVER_POSITION_MIN)

    async def turn_on_switch_device(self, device_id: str) -> None:
        """Turn on a switch or relay device."""

        await self._set_switch_device_state(device_id, True)

    async def turn_off_switch_device(self, device_id: str) -> None:
        """Turn off a switch or relay device."""

        await self._set_switch_device_state(device_id, False)

    async def set_climate_device_preset(self, device_id: str, preset: str) -> None:
        """Set a climate preset/hold mode supported by the target device."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        preset = _validate_supported_value(preset, "preset", device.preset_modes)
        if preset == PRESET_SCHEDULE_OVERRIDE:
            return
        request_data: dict[str, dict[str, Any]]

        if is_fan_coil_model(device.model):
            hold_value = _FAN_COIL_PRESET_HOLD_TYPES.get(
                preset,
                HoldType.FOLLOW_SCHEDULE,
            )
            request_data = {
                "sComm": {"SetHoldType": hold_value}
            }
        elif is_trv_model(device.model):
            request_data = {
                "sComm": {"SetHoldType": _HEAT_ONLY_PRESET_HOLD_TYPES.get(
                    preset,
                    HoldType.FOLLOW_SCHEDULE,
                )}
            }
        elif is_sq610_model(device.model):
            hold_value = _SQ610_PRESET_HOLD_TYPES.get(
                preset,
                HoldType.FOLLOW_SCHEDULE,
            )
            request_data = {
                "sIT600TH": {_SQ610_WRITE_HOLD_TYPE: hold_value}
            }
        else:
            request_data = {
                "sIT600TH": {"SetHoldType": _HEAT_ONLY_PRESET_HOLD_TYPES.get(
                    preset,
                    HoldType.FOLLOW_SCHEDULE,
                )}
            }

        await self._write_device(device, request_data)

    async def set_climate_device_mode(self, device_id: str, mode: str) -> None:
        """Set a climate HVAC mode supported by the target device."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        mode = _validate_supported_value(mode, "mode", device.hvac_modes)
        request_data: dict[str, dict[str, Any]]

        if is_fan_coil_model(device.model):
            request_data = {
                "sTherS": {"SetSystemMode": _FAN_COIL_HVAC_MODES.get(
                    mode,
                    SystemMode.AUTO,
                )}
            }
        elif is_sq610_model(device.model):
            if mode == HVAC_MODE_OFF:
                request_data = {
                    "sIT600TH": {_SQ610_WRITE_HOLD_TYPE: HoldType.STANDBY}
                }
            elif mode in _SQ610_HVAC_MODES:
                payload: dict[str, Any] = {
                    _SQ610_WRITE_SYSTEM_MODE: _SQ610_HVAC_MODES[mode]
                }
                if device.hold_type == int(HoldType.STANDBY):
                    payload[_SQ610_WRITE_HOLD_TYPE] = HoldType.PERMANENT_HOLD
                request_data = {
                    "sIT600TH": payload
                }
            else:
                raise IT600ValidationError(
                    "mode must be one of ['cool', 'heat', 'off'] for SQ610 devices"
                )
        elif is_trv_model(device.model):
            request_data = {
                "sComm": {"SetHoldType": _HEAT_ONLY_HVAC_HOLD_TYPES.get(
                    mode,
                    HoldType.FOLLOW_SCHEDULE,
                )}
            }
        else:
            request_data = {
                "sIT600TH": {"SetHoldType": _HEAT_ONLY_HVAC_HOLD_TYPES.get(
                    mode,
                    HoldType.FOLLOW_SCHEDULE,
                )}
            }

        await self._write_device(device, request_data)

    async def set_climate_device_fan_mode(self, device_id: str, mode: str) -> None:
        """Set an FC600 fan mode supported by the target device."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        if device.fan_modes is None:
            raise IT600ValidationError(f"climate device {device_id!r} does not support fan modes")
        mode = _validate_supported_value(mode, "mode", device.fan_modes)

        request_data = {"sFanS": {"SetFanMode": _FAN_MODES.get(mode, FanMode.OFF)}}

        await self._write_device(device, request_data)

    async def set_climate_device_locked(self, device_id: str, locked: bool) -> None:
        """Enable or disable a climate-device keypad lock."""

        if not isinstance(locked, bool):
            raise TypeError("locked must be a bool")

        device = self._require_device(device_id, self._climate_devices, "climate")
        if is_sq610_model(device.model):
            await self._write_sq610_property(
                device,
                _SQ610_WRITE_LOCK_KEY,
                1 if locked else 0,
            )
            return

        await self._write_device(device, {"sTherUIS": {"SetLockKey": int(locked)}})

    async def set_climate_device_temperature(
        self, device_id: str, setpoint_celsius: float
    ) -> None:
        """Set a climate target temperature in Celsius."""

        device = self._require_device(device_id, self._climate_devices, "climate")
        min_temp, max_temp = _active_temperature_write_range(device)
        setpoint_celsius = _validate_setpoint(
            setpoint_celsius,
            min_temp,
            max_temp,
        )
        rounded_setpoint = int(self.round_to_half(setpoint_celsius) * TEMPERATURE_SCALE)
        request_data: dict[str, dict[str, int]]
        is_cooling = _uses_cooling_setpoint(device)

        if is_fan_coil_model(device.model):
            if is_cooling:
                request_data = {"sTherS": {"SetCoolingSetpoint_x100": rounded_setpoint}}
            else:
                request_data = {"sTherS": {"SetHeatingSetpoint_x100": rounded_setpoint}}
        elif is_trv_model(device.model):
            request_data = {"sTherS": {"SetHeatingSetpoint_x100": rounded_setpoint}}
        elif is_sq610_model(device.model):
            request_data = {
                "sIT600TH": {
                    _SQ610_WRITE_COOLING_SETPOINT
                    if is_cooling
                    else _SQ610_WRITE_HEATING_SETPOINT: rounded_setpoint
                }
            }
        else:
            request_data = {"sIT600TH": {"SetHeatingSetpoint_x100": rounded_setpoint}}

        await self._write_device(device, request_data)

    @staticmethod
    def round_to_half(number: float) -> float:
        """Round a number to the nearest half step."""

        return round(number * 2) / 2

    async def _make_encrypted_request(
        self,
        command: str,
        request_body: dict[str, Any],
        *,
        retry_disconnect: bool = True,
    ) -> dict[str, Any]:
        """Makes encrypted Salus iT600 json request, decrypts and returns response."""

        async with self._lock:
            if self._session is None:
                self._session = aiohttp.ClientSession()
                self._close_session = True

            request_url = f"http://{self._host}:{self._port}/deviceid/{command}"
            request_body_json = json.dumps(request_body)
            retry_attempts = _DISCONNECT_RETRY_ATTEMPTS if retry_disconnect else 1

            if self._debug:
                _LOGGER.debug(
                    "Gateway request: POST %s\n%s\n", request_url, request_body_json
                )

            if self._protocol is not None:
                request_payload = self._protocol.wrap_request(request_body_json)
            else:
                request_payload = self._encryptor.encrypt(request_body_json)

            for attempt in range(retry_attempts):
                if attempt:
                    _LOGGER.debug(
                        "Gateway disconnected during %s request; retrying once",
                        command,
                    )
                    if self._disconnect_retry_delay > 0:
                        await asyncio.sleep(self._disconnect_retry_delay)

                try:
                    async with self._session.post(
                        request_url,
                        data=request_payload,
                        headers={"content-type": "application/json"},
                        timeout=self._client_timeout(),
                    ) as resp:
                        response_bytes = await resp.read()
                        response_status = getattr(resp, "status", 200)

                    _validate_http_status(
                        response_status,
                        command,
                    )
                    _raise_for_gateway_frame(response_bytes, command)

                    try:
                        if self._protocol is not None:
                            response_json_string = self._protocol.unwrap_response(
                                response_bytes
                            )
                        else:
                            response_json_string = self._encryptor.decrypt(
                                response_bytes
                            )
                    except Exception as e:
                        raise IT600CommandError(
                            f"Failed to decrypt gateway response for '{command}' "
                            f"request"
                        ) from e

                    if self._debug:
                        _LOGGER.debug("Gateway response:\n%s\n", response_json_string)

                    response_json = _validate_gateway_response(
                        json.loads(response_json_string),
                        command,
                    )

                    if response_json["status"] != "success":
                        repr_request_body = repr(request_body)
                        repr_response_body = repr(response_json)

                        _LOGGER.debug("%s failed: %s", command, repr_request_body)
                        raise IT600CommandError(
                            f"iT600 gateway rejected '{command}' command with "
                            f"content '{repr_request_body}' and response "
                            f"'{repr_response_body}'"
                        )

                    return response_json
                except client_exceptions.ServerDisconnectedError as e:
                    if attempt < retry_attempts - 1:
                        continue
                    raise IT600ConnectionError(
                        "Error occurred while communicating with iT600 gateway"
                    ) from e
                except TimeoutError as e:
                    _LOGGER.debug("Timeout during %s request to gateway", command)
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
                    _LOGGER.debug("Gateway returned invalid JSON for %s command", command)
                    raise IT600CommandError(
                        "Invalid JSON response received from iT600 gateway"
                    ) from e
                except (
                    IT600CommandError,
                    IT600ConnectionError,
                    IT600UnsupportedFirmwareError,
                ):
                    raise
                except Exception:
                    _LOGGER.exception(
                        "Unexpected error while communicating with iT600 gateway"
                    )
                    raise

            raise IT600ConnectionError(
                "Error occurred while communicating with iT600 gateway"
            )

    async def close(self) -> None:
        """Close the internally owned aiohttp session, if one was created."""

        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Self:
        """Return this gateway for use as an async context manager."""

        return self

    async def __aexit__(self, *exc_info: object) -> None:
        """Close internally owned resources on async context-manager exit."""

        await self.close()
