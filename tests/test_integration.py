import numpy as np

from calo_analyzer.integration import cumulative_heat_trapezoidal


def test_constant_heat_flow_evenly_spaced_matches_analytical():
    time_h = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    heat_flow = np.full_like(time_h, 2.0)  # constant 2 mW/g
    result = cumulative_heat_trapezoidal(time_h, heat_flow, start_time_h=0.5)

    # For constant q, cumulative heat = q * (t - t_start) * 3.6
    expected_from_start = 2.0 * (time_h[2:] - 0.5) * 3.6
    np.testing.assert_allclose(result[2:], expected_from_start)


def test_uneven_time_spacing():
    time_h = np.array([0.5, 0.6, 1.0])
    heat_flow = np.array([1.0, 2.0, 3.0])
    result = cumulative_heat_trapezoidal(time_h, heat_flow, start_time_h=0.5)

    expected = np.array([0.0, 0.54, 4.14])
    np.testing.assert_allclose(result, expected)


def test_integration_excludes_data_before_start_time():
    time_h = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    heat_flow = np.full_like(time_h, 2.0)
    result = cumulative_heat_trapezoidal(time_h, heat_flow, start_time_h=0.5)

    assert np.isnan(result[0])
    assert np.isnan(result[1])
    assert result[2] == 0.0


def test_no_points_at_or_after_start_time_returns_all_nan():
    time_h = np.array([0.0, 0.1, 0.2])
    heat_flow = np.array([1.0, 1.0, 1.0])
    result = cumulative_heat_trapezoidal(time_h, heat_flow, start_time_h=0.5)

    assert np.all(np.isnan(result))


def test_start_time_between_measured_points_interpolates_origin():
    time_h = np.array([0.0, 0.4, 0.6, 1.0])
    heat_flow = np.array([1.0, 2.0, 3.0, 4.0])
    result = cumulative_heat_trapezoidal(time_h, heat_flow, start_time_h=0.5)

    # heat flow at t=0.5 interpolated between (0.4, 2.0) and (0.6, 3.0) -> 2.5
    # partial trapezoid from (0.5, 2.5) to (0.6, 3.0): 0.5*(2.5+3.0)*0.1*3.6 = 0.99
    # next trapezoid from (0.6, 3.0) to (1.0, 4.0): 0.5*(3.0+4.0)*0.4*3.6 = 5.04
    assert np.isnan(result[0])
    assert np.isnan(result[1])
    np.testing.assert_allclose(result[2], 0.99)
    np.testing.assert_allclose(result[3], 0.99 + 5.04)
