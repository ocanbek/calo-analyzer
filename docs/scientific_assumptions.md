# Scientific Assumptions

This document lists the assumptions baked into `calo_analyzer`'s calculations.
It exists so results can be checked against them, not as a substitute for
domain expertise — see [Limitations](#limitations).

## Units

- **Time**: raw input is assumed to be in **seconds** by default; the user
  may declare it as **hours** instead. Internally, everything is converted to
  hours (`Time (h)`) before any calculation happens.
- **Heat flow**: raw input is assumed to be in **mW** by default; the user
  may declare it as **W** instead (`W → mW` is `× 1000`). Internally,
  everything is converted to mW.

See [`units.py`](../src/calo_analyzer/units.py).

## Cement mass normalization

Heat flow (mW) is divided by the user-supplied cement mass (g) to produce
`Normalized heat flow (mW/g)`. Cement mass must be a strictly positive float;
zero or negative values are rejected with a `ValueError`.

## Cumulative heat formula

Cumulative heat is computed with the composite trapezoidal rule. For two
adjacent included points `i-1, i`:

```
ΔH_i = 0.5 × (q_i + q_{i-1}) × Δt × 3.6
```

where `q` is normalized heat flow in mW/g, `Δt = t_i − t_{i-1}` is in hours,
and `ΔH_i` is in J/g. The running sum of `ΔH_i` is `Cumulative heat (J/g)`.

### The 3.6 factor

`1 mW = 0.001 J/s` and `1 h = 3600 s`, so `1 mW·h = 0.001 × 3600 = 3.6 J`.
The formula's average heat flow (mW/g) times Δt (h) is in mW·h/g, and
multiplying by 3.6 converts that to J/g.

Time spacing does not need to be uniform — each interval uses its own `Δt`.

## Integration start time

- Default integration start time is **0.5 h**, on the assumption that the
  first ~30 minutes of a calorimetry run are typically dominated by mixing
  and initial-dissolution artifacts rather than steady hydration heat flow.
  The user can change this value.
- **Exact-start-time interpolation**: integration begins exactly at
  `start_time_h`, not at the nearest measured point. If `start_time_h` falls
  strictly between two measured points, the heat flow at `start_time_h` is
  linearly interpolated and treated as the integration origin (cumulative
  heat = 0 there); the first measured point at or after `start_time_h` then
  receives the resulting partial-trapezoid increment. If `start_time_h`
  lands exactly on a measured point (or at/before the first measured point),
  that point is the origin.
- **Pre-start values are `NaN`, not `0`.** A value of `0` would read as "zero
  heat released by this time," which is false — no cumulative value has
  actually been computed there. `NaN` correctly signals "not computed" and
  is handled gracefully by pandas/Plotly (skipped in plots and in the 24 h /
  48 h summary interpolation).

See [`integration.py`](../src/calo_analyzer/integration.py).

## Limitations

- This is an early MVP. It performs the arithmetic described above and
  nothing more — there is no smoothing, baseline correction, peak/onset
  detection, or outlier rejection. See
  [`future_features.md`](future_features.md) for ideas not yet implemented.
- Duplicate time values (after unit conversion) are treated as an input
  error, since the trapezoidal rule is undefined for a zero-width interval.
- Column and unit selection are manual; the app does not attempt to infer
  units or column meaning from headers or instrument metadata.
- Results should be checked by the user against raw data and, where
  possible, against the calorimeter's own software before being relied on.
