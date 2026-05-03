"""Cover device parsers."""

from __future__ import annotations

from typing import Any

from ..const import SUPPORT_CLOSE, SUPPORT_OPEN, SUPPORT_SET_POSITION
from ..device_models import MODEL_SR600, cover_device_class, model_identifier
from ..models import CoverDevice
from .common import _common_device_args


def parse_cover_device(device_status: dict[str, Any]) -> CoverDevice | None:
    """Parse one cover (roller shutter/blind) device from gateway payload.

    Extracts position, movement state, and capability info from cover-specific
    protocol fields. Skips endpoints disabled via sButtonS.Mode.

    Protocol fields:
    - `sLevelS.CurrentLevel`: Current position (0-100), 0=closed, 100=open
    - `sLevelS.MoveToLevel_f`: Target position as hex string (first 2 chars)
    - `sButtonS.Mode`: Endpoint enabled state (0=disabled)
    """
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    model = model_identifier(device_status)
    if model == MODEL_SR600:
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
        device_class=cover_device_class(model),
    )
