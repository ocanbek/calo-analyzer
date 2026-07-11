"""Time and heat-flow unit conversions.

Assumptions:
- Raw time defaults to seconds; raw heat flow defaults to mW (instrument convention).
- All downstream calculations work in hours and mW (see integration.py).
"""

from typing import Literal

import numpy as np

TimeUnit = Literal["s", "h"]
HeatFlowUnit = Literal["mW", "W"]

DEFAULT_TIME_UNIT: TimeUnit = "s"
DEFAULT_HEAT_FLOW_UNIT: HeatFlowUnit = "mW"

SECONDS_PER_HOUR = 3600.0
MW_PER_W = 1000.0


def convert_time_to_hours(time: np.ndarray, unit: TimeUnit) -> np.ndarray:
    """Convert a time array from seconds or hours to hours."""
    if unit == "s":
        return np.asarray(time, dtype=float) / SECONDS_PER_HOUR
    if unit == "h":
        return np.asarray(time, dtype=float)
    raise ValueError(f"Unsupported time unit: {unit!r}")


def convert_heat_flow_to_mw(heat_flow: np.ndarray, unit: HeatFlowUnit) -> np.ndarray:
    """Convert a heat-flow array from mW or W to mW."""
    if unit == "W":
        return np.asarray(heat_flow, dtype=float) * MW_PER_W
    if unit == "mW":
        return np.asarray(heat_flow, dtype=float)
    raise ValueError(f"Unsupported heat-flow unit: {unit!r}")
