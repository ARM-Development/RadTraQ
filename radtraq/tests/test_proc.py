import radtraq
import pytest
import act


@pytest.mark.mpl_image_compare(tolerance=10)
def test_cloud_mask():
    f = radtraq.tests.sample_files.EXAMPLE_KAZR
    obj = act.io.armfiles.read_netcdf(f)
    ge = obj.resample(time='1min').nearest()
    ge = radtraq.proc.cloud_mask.calc_cloud_mask(ge, 'reflectivity_copol', 'range')
    ge = ge.where(ge['mask2'] == 1)
    display = act.plotting.TimeSeriesDisplay(ge)
    display.plot('reflectivity_copol', cmap='jet')
    display.axes[0].set_ylim([0,20000])
    ge.close()
    return display.fig
