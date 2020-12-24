import radtraq
import pytest
import act
import numpy as np
import matplotlib.pyplot as plt


@pytest.mark.mpl_image_compare(tolerance=10)
def test_plotting():
    f = radtraq.tests.sample_files.EXAMPLE_KAZR
    obj = act.io.armfiles.read_netcdf(f)

    np.seterr(divide = 'ignore') 
    hist, x, y = radtraq.plotting.cfad.calc_cfad(obj,'reflectivity_copol', 'range')
    display = radtraq.plotting.cfad.plot_cfad(hist, x, y)
    return display.figure


@pytest.mark.mpl_image_compare(tolerance=10)
def test_corner_reflector():
    f = radtraq.tests.sample_files.EXAMPLE_RASTER
    obj = act.io.armfiles.read_netcdf(f)
    data = radtraq.plotting.corner_reflector.plot_cr_raster(obj, target_range=478.,
                                                        el_limits=[-0.5, 2.5], noplot=False)

    np.testing.assert_almost_equal(data['max'], 12.03, decimal=2)
    np.testing.assert_almost_equal(data['min'], -64.46, decimal=2)
    np.testing.assert_almost_equal(data['az_max'], 2.30, decimal=2)
    np.testing.assert_almost_equal(data['el_max'], 0.90, decimal=2)
    np.testing.assert_almost_equal(data['el_top'], 1.32, decimal=2)

    fig = plt.gcf()
    return fig
