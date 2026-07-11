"""File loading, column selection, cleaning, and normalization pipeline.

Assumptions:
- Only .csv and .xlsx uploads are supported for the MVP.
- Missing or non-numeric time/heat-flow values are dropped rather than
  imputed; the caller is told how many rows were dropped.
- Time values are expected to be unique after unit conversion; duplicates
  make trapezoidal integration ambiguous and are treated as an input error.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from calo_analyzer.integration import cumulative_heat_trapezoidal
from calo_analyzer.units import (
    DEFAULT_HEAT_FLOW_UNIT,
    DEFAULT_TIME_UNIT,
    HeatFlowUnit,
    TimeUnit,
    convert_heat_flow_to_mw,
    convert_time_to_hours,
)

SUPPORTED_EXTENSIONS = (".csv", ".xlsx")


def load_raw_file(file) -> pd.DataFrame:
    """Load an uploaded CSV or XLSX file into a DataFrame."""
    name = getattr(file, "name", file)
    suffix = Path(str(name)).suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file)
    if suffix == ".xlsx":
        return pd.read_excel(file)
    raise ValueError(
        f"Unsupported file extension: {suffix!r}. Supported extensions: {SUPPORTED_EXTENSIONS}"
    )


def select_columns(
    df: pd.DataFrame,
    time_col: str | None = None,
    heat_flow_col: str | None = None,
) -> tuple[str, str]:
    """Resolve the time and heat-flow columns, defaulting to the first two."""
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least two columns (time and heat flow)")

    columns = list(df.columns)

    if time_col is None:
        time_col = columns[0]
    elif time_col not in df.columns:
        raise ValueError(f"time_col {time_col!r} not found in columns: {columns}")

    if heat_flow_col is None:
        heat_flow_col = columns[1]
    elif heat_flow_col not in df.columns:
        raise ValueError(f"heat_flow_col {heat_flow_col!r} not found in columns: {columns}")

    return time_col, heat_flow_col


@dataclass
class ProcessingResult:
    df: pd.DataFrame
    dropped_rows: int
    was_sorted: bool


def process_calorimetry_data(
    raw_df: pd.DataFrame,
    time_col: str,
    heat_flow_col: str,
    time_unit: TimeUnit = DEFAULT_TIME_UNIT,
    heat_flow_unit: HeatFlowUnit = DEFAULT_HEAT_FLOW_UNIT,
    cement_mass_g: float = 1.0,
    integration_start_h: float = 0.5,
) -> ProcessingResult:
    """Clean, convert, normalize, and integrate raw calorimetry data."""
    if cement_mass_g <= 0:
        raise ValueError(f"cement_mass_g must be positive, got {cement_mass_g}")

    if time_col not in raw_df.columns or heat_flow_col not in raw_df.columns:
        raise ValueError(
            f"time_col {time_col!r} and heat_flow_col {heat_flow_col!r} "
            f"must both be present in columns: {list(raw_df.columns)}"
        )

    time_numeric = pd.to_numeric(raw_df[time_col], errors="coerce")
    heat_flow_numeric = pd.to_numeric(raw_df[heat_flow_col], errors="coerce")

    valid_mask = time_numeric.notna() & heat_flow_numeric.notna()
    dropped_rows = int((~valid_mask).sum())

    time_values = time_numeric[valid_mask].to_numpy(dtype=float)
    heat_flow_values = heat_flow_numeric[valid_mask].to_numpy(dtype=float)

    time_h = convert_time_to_hours(time_values, time_unit)
    heat_flow_mw = convert_heat_flow_to_mw(heat_flow_values, heat_flow_unit)

    sort_order = np.argsort(time_h, kind="stable")
    was_sorted = not np.array_equal(sort_order, np.arange(len(sort_order)))
    time_h = time_h[sort_order]
    heat_flow_mw = heat_flow_mw[sort_order]

    if time_h.size > 1 and np.any(np.diff(time_h) == 0):
        raise ValueError("Duplicate time values found after sorting; cannot integrate.")

    normalized_heat_flow = heat_flow_mw / cement_mass_g

    cumulative_heat = cumulative_heat_trapezoidal(
        time_h, normalized_heat_flow, start_time_h=integration_start_h
    )

    processed_df = pd.DataFrame(
        {
            "Time (h)": time_h,
            "Raw heat flow (mW)": heat_flow_mw,
            "Normalized heat flow (mW/g)": normalized_heat_flow,
            "Cumulative heat (J/g)": cumulative_heat,
        }
    )

    return ProcessingResult(df=processed_df, dropped_rows=dropped_rows, was_sorted=was_sorted)
