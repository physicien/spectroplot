import numpy as np
import sys
sys.path.insert(0, "src")

from hypothesis import given, strategies as st, settings

from spectroplot.functions import (
    wntonm, wntoev, nmtown, nmtoev,
    lineshape, normalization, atLeastTwo,
    plotType, roundup, rounddown, unitConverter,
)
from spectroplot.global_constants import conv_wntoev

# Strategies for property-based converter tests
positive_floats = st.floats(min_value=1, max_value=1e6, allow_infinity=False,
                            allow_nan=False)
positive_nparrays = st.lists(
    st.floats(min_value=1, max_value=1e6, allow_infinity=False, allow_nan=False),
    min_size=1, max_size=10,
).map(np.array)


class TestConverterRoundTrips:
    @given(positive_nparrays)
    @settings(max_examples=100)
    def test_wntonm_nmtown_roundtrip(self, arr):
        result = wntonm(nmtown(arr))
        np.testing.assert_allclose(result, arr, rtol=1e-10)

    @given(positive_nparrays)
    @settings(max_examples=100)
    def test_nmtown_wntonm_roundtrip(self, arr):
        result = nmtown(wntonm(arr))
        np.testing.assert_allclose(result, arr, rtol=1e-10)

    @given(positive_nparrays)
    @settings(max_examples=100)
    def test_nmtoev_via_wn_consistency(self, arr):
        result_direct = nmtoev(arr)
        result_via_wn = wntoev(nmtown(arr))
        np.testing.assert_allclose(result_direct, result_via_wn, rtol=1e-10)

    @given(positive_nparrays)
    @settings(max_examples=100)
    def test_wntoev_via_nm_consistency(self, arr):
        result_direct = wntoev(arr)
        result_via_nm = nmtoev(wntonm(arr))
        np.testing.assert_allclose(result_direct, result_via_nm, rtol=1e-10)

    @given(st.data())
    @settings(max_examples=100)
    def test_wntonm_ev_conversion_consistency(self, data):
        wn = data.draw(st.floats(min_value=100, max_value=50000,
                                 allow_infinity=False, allow_nan=False))
        nm = wntonm(np.array([wn]))[0]
        ev_from_wn = wntoev(np.array([wn]))[0]
        ev_from_nm = nmtoev(np.array([nm]))[0]
        np.testing.assert_allclose(ev_from_wn, ev_from_nm, rtol=1e-10)

    @given(positive_nparrays)
    @settings(max_examples=100)
    def test_unit_converter_identity_out_to_out(self, arr):
        result = unitConverter(arr, ".out", "wn")
        np.testing.assert_allclose(result, arr)

    @given(positive_nparrays)
    @settings(max_examples=100)
    def test_unit_converter_identity_asc_to_asc(self, arr):
        result = unitConverter(arr, ".asc", "nm")
        np.testing.assert_allclose(result, arr)


class TestUnitConverters:
    def test_wntonm(self):
        result = wntonm(np.array([1000, 2000, 5000]))
        expected = np.array([10000, 5000, 2000])
        np.testing.assert_allclose(result, expected)

    def test_wntoev(self):
        result = wntoev(np.array([8065.54, 10000]))
        expected = np.array([1.0, 10000 / 8065.54])
        np.testing.assert_allclose(result, expected)

    def test_nmtown(self):
        result = nmtown(np.array([1000, 500, 200]))
        expected = np.array([10000, 20000, 50000])
        np.testing.assert_allclose(result, expected)

    def test_nmtoev(self):
        result = nmtoev(np.array([806.554, 1000]))
        expected = np.array([1e7 / 806.554 / 8065.54, 1e7 / 1000 / 8065.54])
        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_unit_converter_asc_identity(self):
        data = [400, 500, 600]
        result = unitConverter(np.array(data), ".asc", "nm")
        np.testing.assert_allclose(result, data)

    def test_unit_converter_out_to_nm(self):
        data = [10000, 20000]
        result = unitConverter(np.array(data), ".out", "nm")
        expected = [1000, 500]
        np.testing.assert_allclose(result, expected)

    def test_unit_converter_list_input(self):
        data = [1000, 2000]
        result = wntonm(data)
        np.testing.assert_allclose(result, [10000, 5000])


class TestLineshape:
    def test_lorentzian_at_center(self):
        x_range = np.linspace(900, 1100, 1000)
        result = lineshape(1.0, x_range, 1000, 20, ls_gauss=False)
        assert abs(result[np.argmin(np.abs(x_range - 1000))] - 1.0) < 0.01

    def test_gaussian_at_center(self):
        x_range = np.linspace(900, 1100, 1000)
        result = lineshape(1.0, x_range, 1000, 20, ls_gauss=True)
        assert abs(result[np.argmin(np.abs(x_range - 1000))] - 1.0) < 0.01

    def test_lorentzian_half_max(self):
        x_range = np.array([1000, 1010, 1020])
        result = lineshape(1.0, x_range, 1000, 20, ls_gauss=False)
        np.testing.assert_allclose(result[0], 1.0, atol=0.01)
        np.testing.assert_allclose(result[1], 0.5, atol=0.01)

    def test_lorentzian_zero_at_distance(self):
        x_range = np.array([1000, 2000])
        result = lineshape(1.0, x_range, 1000, 20, ls_gauss=False)
        assert result[0] == 1.0
        assert result[1] < 0.01


class TestNormalization:
    def test_normalization(self):
        data = np.array([0, 5, 10])
        result = normalization(data)
        np.testing.assert_allclose(result, [0.0, 0.5, 1.0])

    def test_normalization_constant(self):
        data = np.array([3, 3, 3])
        result = normalization(data)
        assert np.isnan(result).any()

    def test_normalization_negative(self):
        data = np.array([-5, 0, 5])
        result = normalization(data)
        np.testing.assert_allclose(result, [0.0, 0.5, 1.0])


class TestAtLeastTwo:
    def test_all_true(self):
        assert atLeastTwo(True, True, True) is True

    def test_two_true(self):
        assert atLeastTwo(True, True, False) is True
        assert atLeastTwo(True, False, True) is True
        assert atLeastTwo(False, True, True) is True

    def test_one_true(self):
        assert atLeastTwo(True, False, False) is False
        assert atLeastTwo(False, True, False) is False
        assert atLeastTwo(False, False, True) is False

    def test_none_true(self):
        assert atLeastTwo(False, False, False) is False


class TestPlotType:
    def test_nm(self):
        assert plotType(True, False, False) == ("nm", 10)

    def test_wn(self):
        assert plotType(False, True, False) == ("wn", 1)

    def test_ev(self):
        assert plotType(False, False, True) == ("ev", 1000)

    def test_none_defaults_to_wn(self):
        assert plotType(False, False, False) == ("wn", 1)

    def test_multiple_but_priority(self):
        assert plotType(True, True, False) == ("nm", 10)


class TestRounding:
    def test_roundup_ev(self):
        assert roundup(1.23, True, False, False) == 2.0
        assert roundup(2.0, True, False, False) == 2.0

    def test_roundup_wn(self):
        assert roundup(1234, False, True, False) == 1300
        assert roundup(1200, False, True, False) == 1200

    def test_roundup_nm(self):
        assert roundup(123, False, False, True) == 130
        assert roundup(120, False, False, True) == 120

    def test_rounddown_ev(self):
        assert rounddown(1.23, True, False, False) == 1.0
        assert rounddown(1.0, True, False, False) == 1.0

    def test_rounddown_wn(self):
        assert rounddown(1234, False, True, False) == 1200
        assert rounddown(1200, False, True, False) == 1200

    def test_rounddown_nm(self):
        assert rounddown(127, False, False, True) == 120
        assert rounddown(120, False, False, True) == 120
