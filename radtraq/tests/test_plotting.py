import radtraq
import pytest
import act

@pytest.mark.mpl_image_compare(tolerance=10)
def test_plotting():
    f = radtraq.tests.sample_files.EXAMPLE_KAZR
    obj = act.io.armfiles.read_netcdf(f)

    hist, x, y = radtraq.plotting.cfad.calc_cfad(obj,'reflectivity_copol', 'range')
    display = radtraq.plotting.cfad.plot_cfad(hist, x, y)
    return display.fig
