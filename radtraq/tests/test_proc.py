import radtraq
import pytest
import act
import numpy as np


@pytest.mark.mpl_image_compare(tolerance=10)
def test_cloud_mask():
    f = radtraq.tests.sample_files.EXAMPLE_KAZR
    ge = act.io.armfiles.read_netcdf(f)
    ge = radtraq.proc.cloud_mask.calc_cloud_mask(ge, 'reflectivity_copol')
    ge = ge.where(ge['cloud_mask_2'] == 1)
    display = act.plotting.TimeSeriesDisplay(ge)
    display.plot('reflectivity_copol', cmap='jet')
    display.axes[0].set_ylim([0, 20000])
    ge.close()
    return display.fig


def test_calc_avg_profile():
    variables = ['reflectivity_copol', 'reflectivity_xpol']
    profile_variables = [var + '_avg_prof' for var in variables]
    f = radtraq.tests.sample_files.EXAMPLE_KAZR
    ge = act.io.armfiles.read_netcdf(f)
    ge = radtraq.proc.profile.calc_avg_profile(ge, variables)
    assert np.isclose(np.nansum(ge[profile_variables[0]].values), -1316.9692)
    assert np.isclose(np.nansum(ge[profile_variables[1]].values), -3882.646)


if __name__ == '__main__':
    test_cloud_mask()
    test_calc_avg_profile()
