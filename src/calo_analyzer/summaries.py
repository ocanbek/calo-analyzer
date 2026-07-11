"""24 h / 48 h / final-time cumulative heat summaries.

Assumptions:
- NaN cumulative heat values (e.g. points before the integration start time)
  are excluded from interpolation and from the "final" point.
- `time_h` and `cumulative_heat` are not required to be pre-sorted: both
  `interpolate_at` and `summarize_cumulative_heat` sort by time internally
  before operating, so callers do not need to guarantee ordering.
"""

from dataclasses import dataclass

import numpy as np

TARGET_24H = 24.0
TARGET_48H = 48.0


@dataclass
class CumulativeHeatSummary:
    value_24h: float | None
    value_48h: float | None
    final_time_h: float
    final_value: float
    reached_24h: bool
    reached_48h: bool
    message: str


def _valid_sorted(time_h: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    time_h = np.asarray(time_h, dtype=float)
    values = np.asarray(values, dtype=float)
    valid_mask = ~np.isnan(values)
    if not np.any(valid_mask):
        raise ValueError("No valid (non-NaN) cumulative heat values available.")

    valid_time = time_h[valid_mask]
    valid_values = values[valid_mask]
    order = np.argsort(valid_time, kind="stable")
    return valid_time[order], valid_values[order]


def interpolate_at(time_h: np.ndarray, values: np.ndarray, target_h: float) -> float | None:
    """Linearly interpolate `values` at `target_h`, ignoring NaN entries.

    Returns the exact value if `target_h` matches a valid point, the
    linearly interpolated value if `target_h` falls between two valid
    points, or None if `target_h` is outside the valid time range.
    Raises ValueError if there are no valid (non-NaN) values at all.
    """
    valid_time, valid_values = _valid_sorted(time_h, values)

    if target_h < valid_time[0] or target_h > valid_time[-1]:
        return None

    idx = int(np.searchsorted(valid_time, target_h))
    if valid_time[idx] == target_h:
        return float(valid_values[idx])

    t0, t1 = valid_time[idx - 1], valid_time[idx]
    v0, v1 = valid_values[idx - 1], valid_values[idx]
    frac = (target_h - t0) / (t1 - t0)
    return float(v0 + frac * (v1 - v0))


def summarize_cumulative_heat(time_h: np.ndarray, cumulative_heat: np.ndarray) -> CumulativeHeatSummary:
    """Summarize cumulative heat at 24 h, 48 h, and the final valid point."""
    valid_time, valid_values = _valid_sorted(time_h, cumulative_heat)

    final_time_h = float(valid_time[-1])
    final_value = float(valid_values[-1])

    value_24h = interpolate_at(time_h, cumulative_heat, TARGET_24H)
    value_48h = interpolate_at(time_h, cumulative_heat, TARGET_48H)

    reached_24h = value_24h is not None
    reached_48h = value_48h is not None

    if reached_48h:
        message = "Cumulative heat reported at both 24 h and 48 h."
    elif reached_24h:
        message = (
            f"Experiment ended at {final_time_h:.2f} h, before 48 h. "
            "48 h cumulative heat is not available; showing 24 h and the final recorded value."
        )
    else:
        message = (
            f"Experiment ended at {final_time_h:.2f} h, before 24 h. "
            "Neither 24 h nor 48 h cumulative heat is available; showing the final recorded value."
        )

    return CumulativeHeatSummary(
        value_24h=value_24h,
        value_48h=value_48h,
        final_time_h=final_time_h,
        final_value=final_value,
        reached_24h=reached_24h,
        reached_48h=reached_48h,
        message=message,
    )
