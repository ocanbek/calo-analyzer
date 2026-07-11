import numpy as np
import pytest

from calo_analyzer.summaries import interpolate_at, summarize_cumulative_heat


def test_exact_24h_and_48h_values_returned():
    time_h = np.array([0.0, 12.0, 24.0, 36.0, 48.0])
    cumulative = np.array([0.0, 5.0, 10.0, 15.0, 20.0])
    summary = summarize_cumulative_heat(time_h, cumulative)

    assert summary.value_24h == 10.0
    assert summary.value_48h == 20.0
    assert summary.reached_24h is True
    assert summary.reached_48h is True
    assert summary.final_time_h == 48.0
    assert summary.final_value == 20.0


def test_interpolated_24h_and_48h_when_exact_times_absent():
    time_h = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0])
    cumulative = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0])  # slope = 1
    summary = summarize_cumulative_heat(time_h, cumulative)

    assert summary.value_24h == pytest.approx(24.0)
    assert summary.value_48h == pytest.approx(48.0)


def test_experiment_ends_before_24h_reports_final_value_only():
    time_h = np.array([0.0, 5.0, 10.0])
    cumulative = np.array([0.0, 5.0, 10.0])
    summary = summarize_cumulative_heat(time_h, cumulative)

    assert summary.value_24h is None
    assert summary.value_48h is None
    assert summary.reached_24h is False
    assert summary.reached_48h is False
    assert summary.final_time_h == 10.0
    assert summary.final_value == 10.0
    assert "24" in summary.message or "before" in summary.message


def test_experiment_reaches_24h_but_not_48h():
    time_h = np.array([0.0, 12.0, 24.0, 30.0])
    cumulative = np.array([0.0, 6.0, 12.0, 15.0])
    summary = summarize_cumulative_heat(time_h, cumulative)

    assert summary.value_24h == 12.0
    assert summary.value_48h is None
    assert summary.reached_24h is True
    assert summary.reached_48h is False
    assert summary.final_time_h == 30.0
    assert summary.final_value == 15.0
    assert "48" in summary.message


def test_nan_values_before_integration_start_are_ignored():
    time_h = np.array([0.0, 0.25, 0.5, 12.0, 24.0, 48.0])
    cumulative = np.array([np.nan, np.nan, 0.0, 6.0, 12.0, 24.0])
    summary = summarize_cumulative_heat(time_h, cumulative)

    assert summary.value_24h == 12.0
    assert summary.value_48h == 24.0
    assert summary.final_time_h == 48.0
    assert summary.final_value == 24.0


def test_interpolate_at_target_outside_range_returns_none():
    time_h = np.array([0.0, 10.0, 20.0])
    values = np.array([0.0, 1.0, 2.0])

    assert interpolate_at(time_h, values, 25.0) is None
    assert interpolate_at(time_h, values, -5.0) is None


def test_all_nan_cumulative_heat_raises_value_error():
    time_h = np.array([0.0, 1.0, 2.0])
    values = np.array([np.nan, np.nan, np.nan])

    with pytest.raises(ValueError):
        interpolate_at(time_h, values, 1.0)

    with pytest.raises(ValueError):
        summarize_cumulative_heat(time_h, values)


def test_unsorted_input_is_sorted_internally():
    # Chosen behavior: interpolate_at / summarize_cumulative_heat sort by
    # time internally rather than raising on unsorted input (documented in
    # summaries.py). Points below correspond to a constant slope of 0.5
    # J/g per hour, given out of time order.
    time_h = np.array([24.0, 0.0, 48.0, 12.0])
    cumulative = np.array([12.0, 0.0, 24.0, 6.0])
    summary = summarize_cumulative_heat(time_h, cumulative)

    assert summary.value_24h == 12.0
    assert summary.value_48h == 24.0
    assert summary.final_time_h == 48.0
    assert summary.final_value == 24.0
