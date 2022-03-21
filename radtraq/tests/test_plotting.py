from radtraq.tests.sample_files import EXAMPLE_KAZR
from radtraq.tests.sample_files import EXAMPLE_RASTER
from radtraq.tests.sample_files import EXAMPLE_CSAPR
from radtraq.plotting.cfad import calc_cfad, plot_cfad
from radtraq.plotting.corner_reflector import plot_cr_raster
from radtraq.plotting.self_consistency import plot_self_consistency
import pytest
from act.io.armfiles import read_netcdf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


@pytest.mark.mpl_image_compare(tolerance=10)
def test_plotting():
    obj = read_netcdf(EXAMPLE_KAZR)

    np.seterr(divide='ignore')
    data_array = calc_cfad(obj, 'reflectivity_copol')
    dims = data_array.dims
    display = plot_cfad(data_array, data_array[dims[1]], data_array[dims[0]])
    return display.figure


@pytest.mark.mpl_image_compare(tolerance=10)
def test_corner_reflector():
    obj = read_netcdf(EXAMPLE_RASTER)
    data = plot_cr_raster(obj, target_range=478., el_limits=[-0.5, 2.5], noplot=False)

    np.testing.assert_almost_equal(data['max'], 12.09, decimal=2)
    np.testing.assert_almost_equal(data['min'], -64.89, decimal=2)
    np.testing.assert_almost_equal(data['az_max'], 2.30, decimal=2)
    np.testing.assert_almost_equal(data['el_max'], 0.90, decimal=2)
    np.testing.assert_almost_equal(data['el_top'], 1.38, decimal=2)
    np.testing.assert_almost_equal(data['range'], 478.01, decimal=2)

    assert isinstance(data['fig'], (Figure, ))

    fig = plt.gcf()
    return fig


@pytest.mark.mpl_image_compare(tolerance=10)
def test_self_consistency():
    obj = read_netcdf(EXAMPLE_CSAPR)
    thresh = {'copol_correlation_coeff': 0.99}
    # Set up dictionary of variables to plot
    var_dict = {'differential_reflectivity': {'variable': 'reflectivity', 'bin_width': [1, 0.25], 'linreg': True},
                'specific_differential_phase': {'variable': 'reflectivity'},
                'differential_phase': {'variable': 'reflectivity', 'bin_width': [1, 2.0]},
                'mean_doppler_velocity': {'variable': 'reflectivity', 'bin_width': [1, 0.5]}}

    plot_self_consistency(obj, variables=var_dict, thresh=thresh)
    fig = plt.gcf()
    return fig


if __name__ == '__main__':
    test_plotting()
    test_corner_reflector()
    test_self_consistency()
