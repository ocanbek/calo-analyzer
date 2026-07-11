# Product Spec — Long-Term Vision

**Status: vision document, not a build plan.** This captures the original,
broader product request in full. It is intentionally larger than any single
implementation pass should attempt. The actual build proceeds incrementally
against [`mvp_plan.md`](mvp_plan.md); features listed here beyond the current
MVP are tracked as ideas in [`future_features.md`](future_features.md) and
should be scoped and approved individually before implementation, not
built all at once.

## Original goal

Build a small, clean, testable Python/Streamlit app that allows a user to
upload raw isothermal calorimetry data from CSV or Excel, normalize heat
flow by cement mass, calculate cumulative heat using trapezoidal
integration, plot the results interactively, and show key 24 h / 48 h
cumulative heat values.

## Original constraints

- Keep scientific calculation logic separate from the Streamlit UI.
- Use a proper Python package structure with a `src/` layout.
- Add unit tests with `pytest`.
- Do not build one giant Streamlit script.
- Do not add unnecessary features beyond the MVP.
- Prefer simple, readable code over clever abstractions.
- Use type hints where useful.
- Make assumptions explicit in code and documentation.

## Full original scope (broader than the implemented MVP)

- Upload `.csv`, `.xlsx`, and optionally `.xls`.
- Manual selection of time and heat-flow columns, defaulting to the first
  two columns.
- Time unit toggle (seconds / hours), heat-flow unit toggle (mW / W).
- Cement mass (g), integration start time (h, default 0.5), plot
  time-window maximum (h, default `min(max time, 48h)`).
- Cleaning: drop rows with missing time/heat-flow, report count; sort by
  time if needed, warn if sorting was required; validate monotonic time.
- Cumulative heat via composite trapezoidal rule from the integration start
  time, handling uneven time spacing.
- Two interactive Plotly plots (heat flow vs. time, cumulative heat vs.
  time) with user-adjustable time range and zoom/pan.
- Summary table of cumulative heat at 24 h and 48 h (interpolated when the
  exact time point isn't present), with explicit messaging when the
  experiment doesn't reach one or both of those times.
- **An educational tab** in the Streamlit app: introduction to isothermal
  calorimetry in cement hydration, heat flow vs. cumulative heat, why early
  data is excluded by default, the trapezoidal rule with a worked example,
  and concise references (ASTM C1702, general cement hydration / isothermal
  calorimetry literature, general numerical integration references).
- Unit tests covering unit conversion, normalization, trapezoidal
  integration (even/uneven spacing, start-time exclusion), 24 h/48 h
  summary interpolation and partial-coverage behavior, and cement-mass
  validation.
- A suggested module layout separating `io.py`, `units.py`, `processing.py`,
  `integration.py`, `summaries.py`, `plotting.py`, and a UI-only
  `streamlit_app.py`.

## What actually shipped as the MVP (see mvp_plan.md)

A trimmed version of the above: CSV/XLSX upload, manual column and unit
selection, cement-mass normalization, trapezoidal cumulative heat with
exact-start-time interpolation, two Plotly plots, a 24 h/48 h summary table,
and a processed-data CSV download — built as `units.py`, `processing.py`
(which also owns file loading and column selection), `integration.py`,
`summaries.py`, and a UI-only `streamlit_app.py` (which builds the Plotly
figures inline rather than in a separate `plotting.py`). The educational tab,
`.xls` support, and a dedicated `io.py`/`plotting.py` split were deferred —
see [`future_features.md`](future_features.md).
