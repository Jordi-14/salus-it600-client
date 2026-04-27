"""Salus device model and protocol helpers."""

from __future__ import annotations

from typing import Any

MODEL_FC600 = "FC600"
MODEL_SP600 = "SP600"
MODEL_SPE600 = "SPE600"
MODEL_SW600 = "SW600"
MODEL_OS600 = "OS600"
MODEL_WLS600 = "WLS600"
MODEL_SMOKE_SENSOR = "SmokeSensor-EM"
MODEL_MINI_TRV = "it600MINITRV"
MODEL_RECEIVER = "it600Receiver"
MODEL_BUTTON = "SB600"

SQ610_MODEL_TOKEN = "SQ610"

BINARY_RELAY_MODELS = {MODEL_MINI_TRV, MODEL_RECEIVER}
BINARY_SENSOR_DEVICE_CLASSES = {
    MODEL_SW600: "window",
    MODEL_OS600: "window",
    MODEL_WLS600: "moisture",
    MODEL_SMOKE_SENSOR: "smoke",
    MODEL_MINI_TRV: "valve",
    MODEL_RECEIVER: "receiver",
}
OUTLET_MODELS = {MODEL_SP600, MODEL_SPE600}
SKIPPED_BINARY_SENSOR_MODELS = {MODEL_BUTTON}

SQ610_MODE_AUTO = 1
SQ610_MODE_COOL = 3
SQ610_MODE_HEAT = 4
SQ610_MODE_EMERGENCY_HEAT = 5

SQ610_HOLD_AUTO = 0
SQ610_HOLD_PERMANENT = 2
SQ610_HOLD_STANDBY = 7

SQ610_RUNNING_HEAT = 1
SQ610_RUNNING_COOL = 2

SQ610_WRITE_HEATING_SETPOINT = "SetHeatingSetpoint_x100"
SQ610_WRITE_COOLING_SETPOINT = "SetCoolingSetpoint_x100"
SQ610_WRITE_HOLD_TYPE = "SetHoldType"
SQ610_WRITE_SYSTEM_MODE = "SetSystemMode"


def model_identifier(device_status: dict[str, Any]) -> str | None:
    """Return the device model identifier from a detailed gateway payload."""
    model = device_status.get("DeviceL", {}).get("ModelIdentifier_i")
    return model if isinstance(model, str) else None


def basic_model_identifier(device_status: dict[str, Any]) -> str | None:
    """Return the model identifier from a readall summary payload."""
    basic = device_status.get("sBasicS")
    if not isinstance(basic, dict):
        return None
    model = basic.get("ModelIdentifier")
    return model if isinstance(model, str) else None


def is_sq610_model(model: str | None) -> bool:
    """Return whether a model identifier is an SQ610 Quantum thermostat."""
    return isinstance(model, str) and SQ610_MODEL_TOKEN in model.upper()


def is_fan_coil_model(model: str | None) -> bool:
    """Return whether a model identifier is an FC600 fan-coil thermostat."""
    return model == MODEL_FC600


def is_binary_sensor_summary(device_status: dict[str, Any]) -> bool:
    """Return whether a readall entry describes a binary sensor."""
    return "sIASZS" in device_status or basic_model_identifier(device_status) in BINARY_RELAY_MODELS


def binary_sensor_device_class(model: str | None) -> str | None:
    """Return the Home Assistant-style binary sensor device class."""
    return BINARY_SENSOR_DEVICE_CLASSES.get(model)


def switch_device_class(model: str | None) -> str:
    """Return the Home Assistant-style switch device class."""
    return "outlet" if model in OUTLET_MODELS else "switch"
