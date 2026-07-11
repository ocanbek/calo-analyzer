"""Trapezoidal cumulative heat integration.

Assumptions:
- `time_h` is sorted strictly ascending (callers, e.g. processing.py, are
  responsible for sorting/validating before calling this function).
- Points before `start_time_h` are excluded from the integral and reported as
  NaN, not 0 — NaN signals "not computed", whereas 0 would misleadingly read
  as "zero heat released" at that time.
- Integration begins exactly at `start_time_h`, not at the nearest measured
  point. If `start_time_h` falls strictly between two measured points, the
  heat flow at `start_time_h` is linearly interpolated and used as the
  integration origin (cumulative heat 0.0 there); the first measured point at
  or after `start_time_h` then receives the resulting partial-trapezoid
  increment. If `start_time_h` lands exactly on a measured point, or at/before
  the first measured point, that point is the origin.
"""

import numpy as np

J_PER_MWH = 3.6  # 1 mW * 1 h = 0.001 J/s * 3600 s = 3.6 J


def cumulative_heat_trapezoidal(
    time_h: np.ndarray,
    heat_flow_mw_per_g: np.ndarray,
    start_time_h: float = 0.5,
) -> np.ndarray:
    """Compute cumulative heat (J/g) via the composite trapezoidal rule.

    For adjacent included points i-1, i:
        dH_i = 0.5 * (q_i + q_{i-1}) * (t_i - t_{i-1}) * 3.6
    where q is normalized heat flow in mW/g and t is time in hours.
    """
    time_h = np.asarray(time_h, dtype=float)
    heat_flow_mw_per_g = np.asarray(heat_flow_mw_per_g, dtype=float)
    if time_h.shape != heat_flow_mw_per_g.shape:
        raise ValueError("time_h and heat_flow_mw_per_g must have the same shape")

    n = time_h.shape[0]
    cumulative = np.full(n, np.nan)
    if n == 0:
        return cumulative

    if start_time_h <= time_h[0]:
        start_idx = 0
        cumulative[0] = 0.0
    else:
        included = np.flatnonzero(time_h >= start_time_h)
        if included.size == 0:
            return cumulative
        start_idx = int(included[0])
        if time_h[start_idx] == start_time_h:
            cumulative[start_idx] = 0.0
        else:
            prev_idx = start_idx - 1
            t0, t1 = time_h[prev_idx], time_h[start_idx]
            q0, q1 = heat_flow_mw_per_g[prev_idx], heat_flow_mw_per_g[start_idx]
            frac = (start_time_h - t0) / (t1 - t0)
            q_start = q0 + frac * (q1 - q0)
            dt = t1 - start_time_h
            avg_q = 0.5 * (q1 + q_start)
            cumulative[start_idx] = avg_q * dt * J_PER_MWH

    for idx in range(start_idx + 1, n):
        dt = time_h[idx] - time_h[idx - 1]
        avg_q = 0.5 * (heat_flow_mw_per_g[idx] + heat_flow_mw_per_g[idx - 1])
        cumulative[idx] = cumulative[idx - 1] + avg_q * dt * J_PER_MWH

    return cumulative
