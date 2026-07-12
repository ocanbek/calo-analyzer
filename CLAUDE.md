# calo-analyzer

Streamlit app for isothermal calorimetry (cement hydration) data analysis.
Early MVP — see README.md for what it does.

## Architecture

Scientific logic lives in `src/calo_analyzer/` (`units.py`, `processing.py`,
`integration.py`, `summaries.py`) and must stay independent of Streamlit.
`app/streamlit_app.py` is UI-only — it calls into the package and renders
results, but never reimplements a calculation.

## Commands

    source .venv/bin/activate
    pytest                              # run tests
    ruff check .                        # lint
    ruff format .                       # format
    streamlit run app/streamlit_app.py  # launch the app

## Known issue — pandas/pyarrow pin

pandas 3.0.x + pyarrow 25.x segfaulted Streamlit's Arrow serialization on
this machine (crashed on any widget rerun, e.g. the Cement mass input).
`pyproject.toml` pins `pandas<3` and a compatible `pyarrow` range. Don't
loosen this pin without re-testing a full upload → widget-interaction cycle
through a real browser.

## Docs map

- `docs/scientific_assumptions.md` — source of truth for formulas/units.
- `docs/product_spec.md` — long-term vision; NOT a build queue.
- `docs/future_features.md` — deferred ideas, unscoped.
- `docs/mvp_plan.md` — what's actually implemented.

## Constraints

- Don't add features beyond what's explicitly requested.
- Any change to `integration.py`, `processing.py`, or `summaries.py` needs
  matching tests.
- Run `ruff check .` and `ruff format .` before considering a change done.
