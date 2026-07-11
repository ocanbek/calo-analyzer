# calo-analyzer

A small Streamlit app for analyzing isothermal calorimetry data from cement
hydration measurements: upload raw heat-flow data, normalize it by cement
mass, integrate cumulative heat, and view the results interactively.

> **Early MVP — check the outputs.** This app performs a specific, documented
> set of conversions and calculations (see
> [Scientific assumptions](#scientific-assumptions) below) and nothing more.
> There is no smoothing, baseline correction, or automated sanity-checking
> of your data. Always sanity-check results against your raw data before
> relying on them.

## What it does

1. Upload raw calorimetry data (CSV or XLSX).
2. Select which column is time and which is heat flow (defaults to the
   first two columns).
3. Declare the input units (time: seconds or hours; heat flow: mW or W).
4. Enter cement mass (g), integration start time (h), and a plot time
   window.
5. The app normalizes heat flow by cement mass, integrates cumulative heat
   with the composite trapezoidal rule, and shows:
   - an interactive normalized heat-flow vs. time plot
   - an interactive cumulative heat vs. time plot
   - cumulative heat at 24 h and 48 h (interpolated if needed), plus the
     final recorded value
   - a downloadable CSV of the processed data

## Current MVP features

- CSV/XLSX upload with manual or default column selection.
- Time unit conversion (s ↔ h) and heat-flow unit conversion (mW ↔ W).
- Cement-mass normalization with validation (mass must be > 0).
- Missing/non-numeric row cleaning, with a reported drop count.
- Automatic sorting by time with a warning if the input wasn't sorted.
- Duplicate-time rejection (ambiguous for integration).
- Trapezoidal cumulative heat integration starting exactly at the chosen
  start time (default 0.5 h), including interpolation when that time falls
  between two measured points.
- Two interactive Plotly plots with zoom/pan.
- 24 h / 48 h cumulative heat summary with clear messaging when the
  experiment doesn't reach one or both of those times.
- Processed-data preview and CSV download.

## Quickstart

Requires Python 3.10+.

```bash
# 1. create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. install the package with dev dependencies (pytest)
pip install -e ".[dev]"

# 3. run the tests
pytest

# 4. launch the app
streamlit run app/streamlit_app.py
```

Then open the URL Streamlit prints (typically `http://localhost:8501`).

To try it immediately without your own data, upload
[`examples/sample_calo_data.csv`](examples/sample_calo_data.csv) — a small
synthetic dataset (time in seconds, heat flow in mW, ~54 hours) that exists
purely to exercise the app end to end; it is not real experimental data.

## Expected input format

A CSV or XLSX file with at least two columns:

- a **time** column (numeric)
- a **heat-flow** column (numeric)

Column names can be anything — you pick which column is which in the app.
If you don't pick explicitly, the first column is assumed to be time and
the second is assumed to be heat flow. Rows with missing or non-numeric
values in either column are dropped (and the app reports how many).

## Scientific assumptions

- **Time** defaults to **seconds**; you can declare it as hours instead.
- **Heat flow** defaults to **mW**; you can declare it as W instead
  (`W → mW` is `× 1000`). All internal calculations use hours and mW.
- Cumulative heat is computed with the composite trapezoidal rule. For
  adjacent included points `i-1, i`:

  ```
  ΔH_i = 0.5 × (q_i + q_{i-1}) × Δt × 3.6
  ```

  where `q` is normalized heat flow (mW/g), `Δt` is the time step in hours,
  and `ΔH_i` is in J/g. The `3.6` factor converts mW·h to J
  (`1 mW = 0.001 J/s`, `1 h = 3600 s`, so `1 mW·h = 3.6 J`).
- Integration starts at 0.5 h by default, on the assumption that early data
  is dominated by mixing artifacts rather than steady hydration heat flow.
  Points before the start time are `NaN`, not `0` — see
  [`docs/scientific_assumptions.md`](docs/scientific_assumptions.md) for why.

Full detail — including exact-start-time interpolation behavior and
limitations — is in
[`docs/scientific_assumptions.md`](docs/scientific_assumptions.md).

## Current limitations

- No smoothing, baseline correction, or outlier rejection — raw (cleaned)
  data is used as-is.
- No peak, onset, or acceleration/deceleration detection.
- No multi-sample comparison; one file at a time.
- Export is CSV only (no Excel or PDF report).
- Column and unit selection are manual; the app does not infer them from
  file headers or instrument metadata.
- `.xls` (legacy Excel) is not supported, only `.csv` and `.xlsx`.
- No educational/reference tab in the app yet.
- UI testing so far is a scripted smoke test through the same
  upload → process → summarize call path the app uses, not an automated
  browser click-through.

See [`docs/scientific_assumptions.md`](docs/scientific_assumptions.md) for
the underlying calculation assumptions and their rationale.

## Roadmap

Ideas under consideration for future work — none are scoped or approved
yet, see [`docs/future_features.md`](docs/future_features.md) for the full,
unordered list: smoothing, baseline correction, peak/onset detection,
multi-sample comparison, Excel/PDF export, an in-app educational tab with
references (e.g. ASTM C1702), and better browser-level UI tests.

## Screenshots

None checked in yet — see [`docs/images/README.md`](docs/images/README.md)
for how to add one.

## Further reading

- [`docs/scientific_assumptions.md`](docs/scientific_assumptions.md) —
  units, formulas, and integration behavior in detail.
- [`docs/mvp_plan.md`](docs/mvp_plan.md) — implemented architecture.
- [`docs/product_spec.md`](docs/product_spec.md) — long-term product vision.
- [`docs/future_features.md`](docs/future_features.md) — deferred ideas.
