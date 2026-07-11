# MVP Plan — Implemented Architecture

This summarizes what was actually built, as the trimmed-scope counterpart to
the long-term vision in [`product_spec.md`](product_spec.md).

## Architecture

Scientific logic lives entirely in `src/calo_analyzer/`, independent of
Streamlit. `app/streamlit_app.py` is a thin UI layer that only calls into
that package and renders results — it holds no calculation logic.

Data flow: upload → column/unit selection → sample inputs (cement mass,
integration start, plot max) → `process_calorimetry_data` (clean, convert,
normalize, integrate) → `summarize_cumulative_heat` → plots + summary table
+ CSV download.

## Modules

- **`units.py`** — `convert_time_to_hours`, `convert_heat_flow_to_mw`, and
  the default units (`s`, `mW`).
- **`integration.py`** — `cumulative_heat_trapezoidal`: composite
  trapezoidal integration with exact-start-time interpolation and NaN
  before the start time (see
  [`scientific_assumptions.md`](scientific_assumptions.md)).
- **`processing.py`** — `load_raw_file` (CSV/XLSX), `select_columns`
  (defaults to the first two columns), `process_calorimetry_data`
  (validation, cleaning with dropped-row reporting, sorting with a
  `was_sorted` flag, duplicate-time rejection, normalization, and calling
  `integration.py`), returning a `ProcessingResult`.
- **`summaries.py`** — `interpolate_at` and `summarize_cumulative_heat`:
  24 h / 48 h / final-time cumulative heat summary with linear
  interpolation and partial-coverage messaging, via `CumulativeHeatSummary`.
- **`app/streamlit_app.py`** — file upload, column/unit selection, sample
  inputs, calls into the package, two Plotly figures (heat flow and
  cumulative heat vs. time), summary table, processed-data preview and CSV
  download.

## Completed steps

1. Package skeleton, `units.py`, `integration.py`, and their tests.
2. `processing.py` (load/select/clean/normalize/orchestrate) and its tests.
3. `summaries.py` and its tests.
4. `streamlit_app.py` UI wiring, smoke-tested against a synthetic 50 h
   dataset through the same call path the UI uses.
5. Documentation (this set of docs) and README.

27 tests pass across `test_units.py`, `test_integration.py`,
`test_processing.py`, and `test_summaries.py`.

## Deliberate scope cuts from the original spec

- No `io.py` or `plotting.py` split — file loading/column selection live in
  `processing.py`, and Plotly figures are built inline in
  `streamlit_app.py`. Both are simple enough that the extra file would add
  indirection without benefit at this size.
- No educational tab, no ASTM/reference section, no `.xls` support.
- No smoothing, baseline correction, peak/onset detection, or export
  formats beyond CSV.

See [`future_features.md`](future_features.md) for what's deferred, and
[`product_spec.md`](product_spec.md) for the full original vision.
