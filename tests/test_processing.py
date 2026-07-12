import numpy as np
import pandas as pd
import pytest

from calo_analyzer.processing import process_calorimetry_data, select_columns


def test_select_columns_defaults_to_first_two():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    assert select_columns(df) == ("a", "b")


def test_select_columns_explicit_selection():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    assert select_columns(df, time_col="c", heat_flow_col="a") == ("c", "a")


def test_select_columns_missing_column_raises():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    with pytest.raises(ValueError):
        select_columns(df, time_col="nonexistent")


def test_select_columns_fewer_than_two_columns_raises():
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(ValueError):
        select_columns(df)


def test_normalization_correct():
    df = pd.DataFrame({"time_s": [0, 1800, 3600], "hf_mw": [10.0, 20.0, 30.0]})
    result = process_calorimetry_data(
        df,
        "time_s",
        "hf_mw",
        time_unit="s",
        heat_flow_unit="mW",
        cement_mass_g=5.0,
        integration_start_h=0.0,
    )
    np.testing.assert_allclose(result.df["Normalized heat flow (mW/g)"], [2.0, 4.0, 6.0])


def test_missing_and_non_numeric_rows_dropped_and_counted():
    df = pd.DataFrame({"t": [0, 600, "bad", 1800], "q": [1.0, 2.0, 3.0, np.nan]})
    result = process_calorimetry_data(df, "t", "q", cement_mass_g=1.0, integration_start_h=0.0)
    assert result.dropped_rows == 2
    assert len(result.df) == 2


def test_unsorted_input_is_sorted_and_reports_was_sorted():
    df = pd.DataFrame({"t": [3600, 0, 1800], "q": [3.0, 1.0, 2.0]})
    result = process_calorimetry_data(df, "t", "q", cement_mass_g=1.0, integration_start_h=0.0)
    assert result.was_sorted is True
    np.testing.assert_allclose(result.df["Time (h)"], [0.0, 0.5, 1.0])


def test_duplicate_time_after_conversion_raises():
    df = pd.DataFrame({"t": [0, 0, 3600], "q": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError):
        process_calorimetry_data(df, "t", "q", cement_mass_g=1.0, integration_start_h=0.0)


def test_zero_or_negative_cement_mass_raises():
    df = pd.DataFrame({"t": [0, 1800, 3600], "q": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError):
        process_calorimetry_data(df, "t", "q", cement_mass_g=0.0)
    with pytest.raises(ValueError):
        process_calorimetry_data(df, "t", "q", cement_mass_g=-5.0)


def test_cumulative_heat_column_produced_via_integration():
    df = pd.DataFrame({"t": [0, 1800, 3600], "q": [10.0, 10.0, 10.0]})
    result = process_calorimetry_data(df, "t", "q", cement_mass_g=5.0, integration_start_h=0.0)
    # normalized heat flow constant at 2 mW/g -> cumulative = 2 * t_h * 3.6
    np.testing.assert_allclose(result.df["Cumulative heat (J/g)"], [0.0, 3.6, 7.2])
    np.testing.assert_allclose(result.df["Raw heat flow (mW)"], [10.0, 10.0, 10.0])
