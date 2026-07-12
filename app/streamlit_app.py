"""Streamlit UI for calo-analyzer.

Thin UI layer only: all scientific logic lives in the calo_analyzer package
(processing, integration, summaries). This file wires widgets to that
package and renders results — it does not reimplement any calculation.
"""

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from calo_analyzer.processing import (
    ProcessingResult,
    load_raw_file,
    process_calorimetry_data,
    select_columns,
)
from calo_analyzer.summaries import summarize_cumulative_heat
from calo_analyzer.units import DEFAULT_HEAT_FLOW_UNIT, DEFAULT_TIME_UNIT, HeatFlowUnit, TimeUnit

DEFAULT_CEMENT_MASS_G = 6.0
DEFAULT_INTEGRATION_START_H = 0.5
DEFAULT_PLOT_MAX_H = 48.0

TIME_UNIT_OPTIONS: list[TimeUnit] = ["s", "h"]
HEAT_FLOW_UNIT_OPTIONS: list[HeatFlowUnit] = ["mW", "W"]


@dataclass
class ColumnConfig:
    time_col: str
    heat_flow_col: str
    time_unit: TimeUnit
    heat_flow_unit: HeatFlowUnit


@dataclass
class SampleConfig:
    cement_mass_g: float
    integration_start_h: float
    plot_max_h: float


def render_file_upload() -> pd.DataFrame | None:
    uploaded_file = st.file_uploader("Upload calorimetry data", type=["csv", "xlsx"])
    if uploaded_file is None:
        return None
    try:
        return load_raw_file(uploaded_file)
    except ValueError as exc:
        st.error(str(exc))
        return None


def render_column_and_unit_selection(df: pd.DataFrame) -> ColumnConfig:
    st.subheader("Columns and units")
    columns = list(df.columns)
    default_time_col, default_heat_flow_col = select_columns(df)

    col1, col2 = st.columns(2)
    with col1:
        time_col = st.selectbox("Time column", columns, index=columns.index(default_time_col))
        time_unit = st.selectbox(
            "Time unit", TIME_UNIT_OPTIONS, index=TIME_UNIT_OPTIONS.index(DEFAULT_TIME_UNIT)
        )
    with col2:
        heat_flow_col = st.selectbox(
            "Heat-flow column", columns, index=columns.index(default_heat_flow_col)
        )
        heat_flow_unit = st.selectbox(
            "Heat-flow unit",
            HEAT_FLOW_UNIT_OPTIONS,
            index=HEAT_FLOW_UNIT_OPTIONS.index(DEFAULT_HEAT_FLOW_UNIT),
        )

    return ColumnConfig(
        time_col=time_col,
        heat_flow_col=heat_flow_col,
        time_unit=time_unit,
        heat_flow_unit=heat_flow_unit,
    )


def _estimate_max_time_h(df: pd.DataFrame, column_config: ColumnConfig) -> float | None:
    """Best-effort estimate of the data's max time in hours, used to default the plot-max input."""
    time_numeric = pd.to_numeric(df[column_config.time_col], errors="coerce").dropna()
    if time_numeric.empty:
        return None
    max_raw = float(time_numeric.max())
    return max_raw / 3600.0 if column_config.time_unit == "s" else max_raw


def render_sample_inputs(df: pd.DataFrame, column_config: ColumnConfig) -> SampleConfig:
    st.subheader("Sample and integration settings")
    max_time_h = _estimate_max_time_h(df, column_config)
    default_plot_max_h = min(max_time_h, DEFAULT_PLOT_MAX_H) if max_time_h else DEFAULT_PLOT_MAX_H

    col1, col2, col3 = st.columns(3)
    with col1:
        cement_mass_g = st.number_input(
            "Cement mass (g)",
            min_value=0.001,
            value=float(DEFAULT_CEMENT_MASS_G),
            step=0.1,
        )
    with col2:
        integration_start_h = st.number_input(
            "Integration start time (h)",
            min_value=0.0,
            value=float(DEFAULT_INTEGRATION_START_H),
            step=0.1,
        )
    with col3:
        plot_max_h = st.number_input(
            "Plot time-window max (h)",
            min_value=0.0,
            value=float(default_plot_max_h),
            step=1.0,
        )

    return SampleConfig(
        cement_mass_g=float(cement_mass_g),
        integration_start_h=float(integration_start_h),
        plot_max_h=float(plot_max_h),
    )


def run_processing(
    raw_df: pd.DataFrame, column_config: ColumnConfig, sample_config: SampleConfig
) -> ProcessingResult | None:
    if sample_config.cement_mass_g <= 0:
        st.error(f"Cement mass must be positive, got {sample_config.cement_mass_g}.")
        return None

    try:
        result = process_calorimetry_data(
            raw_df,
            time_col=column_config.time_col,
            heat_flow_col=column_config.heat_flow_col,
            time_unit=column_config.time_unit,
            heat_flow_unit=column_config.heat_flow_unit,
            cement_mass_g=sample_config.cement_mass_g,
            integration_start_h=sample_config.integration_start_h,
        )
    except ValueError as exc:
        st.error(str(exc))
        return None

    if result.dropped_rows > 0:
        st.warning(
            f"Dropped {result.dropped_rows} row(s) with missing or non-numeric time/heat-flow "
            "values."
        )
    if result.was_sorted:
        st.warning("Input data was not sorted by time; it has been sorted automatically.")

    return result


def render_plots(processed_df: pd.DataFrame, plot_max_h: float) -> None:
    st.subheader("Plots")
    x_range = [0, plot_max_h] if plot_max_h else None

    heat_flow_fig = go.Figure()
    heat_flow_fig.add_trace(
        go.Scatter(
            x=processed_df["Time (h)"],
            y=processed_df["Normalized heat flow (mW/g)"],
            mode="lines",
            name="Heat flow",
        )
    )
    heat_flow_fig.update_layout(
        xaxis_title="Time (h)", yaxis_title="Normalized heat flow (mW/g)", xaxis_range=x_range
    )
    st.plotly_chart(heat_flow_fig, use_container_width=True)

    cumulative_fig = go.Figure()
    cumulative_fig.add_trace(
        go.Scatter(
            x=processed_df["Time (h)"],
            y=processed_df["Cumulative heat (J/g)"],
            mode="lines",
            name="Cumulative heat",
        )
    )
    cumulative_fig.update_layout(
        xaxis_title="Time (h)", yaxis_title="Cumulative heat (J/g)", xaxis_range=x_range
    )
    st.plotly_chart(cumulative_fig, use_container_width=True)


def render_summary(processed_df: pd.DataFrame) -> None:
    st.subheader("Cumulative heat summary")
    try:
        summary = summarize_cumulative_heat(
            processed_df["Time (h)"].to_numpy(), processed_df["Cumulative heat (J/g)"].to_numpy()
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    summary_table = pd.DataFrame(
        {
            "Metric": [
                "Cumulative heat at 24 h (J/g)",
                "Cumulative heat at 48 h (J/g)",
                f"Final recorded cumulative heat (J/g) at {summary.final_time_h:.2f} h",
            ],
            "Value": [
                f"{summary.value_24h:.2f}" if summary.value_24h is not None else "Not available",
                f"{summary.value_48h:.2f}" if summary.value_48h is not None else "Not available",
                f"{summary.final_value:.2f}",
            ],
        }
    )
    st.table(summary_table)
    st.info(summary.message)


def render_data_preview(processed_df: pd.DataFrame) -> None:
    st.subheader("Processed data")
    st.dataframe(processed_df, use_container_width=True)
    csv_bytes = processed_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download processed CSV",
        data=csv_bytes,
        file_name="processed_calorimetry_data.csv",
        mime="text/csv",
    )


def main() -> None:
    st.set_page_config(page_title="Calo Analyzer")
    st.title("Calo Analyzer")

    raw_df = render_file_upload()
    if raw_df is None:
        st.info("Upload a CSV or XLSX file to get started.")
        return

    st.subheader("Detected columns")
    st.write(list(raw_df.columns))
    st.dataframe(raw_df.head(), use_container_width=True)

    column_config = render_column_and_unit_selection(raw_df)
    sample_config = render_sample_inputs(raw_df, column_config)

    result = run_processing(raw_df, column_config, sample_config)
    if result is None:
        return

    render_plots(result.df, sample_config.plot_max_h)
    render_summary(result.df)
    render_data_preview(result.df)


if __name__ == "__main__":
    main()
