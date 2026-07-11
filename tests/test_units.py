import numpy as np

from calo_analyzer.units import convert_heat_flow_to_mw, convert_time_to_hours


def test_convert_time_seconds_to_hours():
    time_s = np.array([0.0, 3600.0, 7200.0])
    result = convert_time_to_hours(time_s, "s")
    np.testing.assert_allclose(result, [0.0, 1.0, 2.0])


def test_convert_time_hours_passthrough():
    time_h = np.array([0.5, 1.0, 2.5])
    result = convert_time_to_hours(time_h, "h")
    np.testing.assert_allclose(result, time_h)


def test_convert_heat_flow_w_to_mw():
    heat_flow_w = np.array([0.005, 0.01])
    result = convert_heat_flow_to_mw(heat_flow_w, "W")
    np.testing.assert_allclose(result, [5.0, 10.0])


def test_convert_heat_flow_mw_passthrough():
    heat_flow_mw = np.array([5.0, 10.0])
    result = convert_heat_flow_to_mw(heat_flow_mw, "mW")
    np.testing.assert_allclose(result, heat_flow_mw)
