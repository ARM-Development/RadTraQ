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


def test_extract_profile():
    drop_variables = ['base_time', 'time_offset', 'longitude', 'latitude',
                      'altitued', 'altitude_agl']
    drop_variables = []
    f = radtraq.tests.sample_files.EXAMPLE_PPI
    obj = act.io.armfiles.read_netcdf(f, drop_variables=drop_variables)
    profile_obj = radtraq.proc.profile.extract_profile(obj, azimuth=124, ground_dist=13094,
                                                       ground_range_units='m')
    assert np.isclose(np.nansum(profile_obj['co_to_crosspol_correlation_coeff'].values), 0.168616)
    assert np.isclose(np.nansum(profile_obj['mean_doppler_velocity'].values), 1.6327)

    variables = ['reflectivity', 'co_to_crosspol_correlation_coeff', 'mean_doppler_velocity']
    profile_obj = radtraq.proc.profile.extract_profile(obj, azimuth=124,
                                                       ground_dist=13094, variables=variables)
    assert (set(profile_obj.keys()) - set(variables)) == set(['lat', 'lon', 'alt'])


def test_extract_profile_at_lat_lon():
    drop_variables = ['base_time', 'time_offset', 'longitude', 'latitude',
                      'altitued', 'altitude_agl']
    drop_variables = []
    f = radtraq.tests.sample_files.EXAMPLE_PPI
    obj = act.io.armfiles.read_netcdf(f, drop_variables=drop_variables)
    profile_obj = radtraq.proc.profile.extract_profile_at_lat_lon(obj, 29.68, -95.08)
    assert np.isclose(np.nansum(profile_obj['co_to_crosspol_correlation_coeff'].values), 0.683899)
    assert np.isclose(np.nansum(profile_obj['mean_doppler_velocity'].values), -3.03363)

    variables = ['reflectivity', 'co_to_crosspol_correlation_coeff', 'mean_doppler_velocity']
    profile_obj = radtraq.proc.profile.extract_profile_at_lat_lon(obj, 29.68, -95.08,
                                                                  variables=variables)

    assert (set(profile_obj.keys()) - set(variables)) == set(['lat', 'lon', 'alt'])
    assert profile_obj['height'].attrs['units'] == 'm'


def test_extract_rhi_profile():
    f = radtraq.tests.sample_files.EXAMPLE_RHI
    obj = act.io.armfiles.read_netcdf(f)
    extracted_obj = radtraq.proc.profile.extract_rhi_profile(obj, variables='reflectivity')
    assert np.isclose(np.nansum(extracted_obj['azimuth'].values), 809.95)
    assert np.isclose(np.nansum(extracted_obj['elevation'].values), 540.11)
    assert np.isclose(np.nansum(extracted_obj['reflectivity'].values), -201440.19)

    extracted_obj = radtraq.proc.profile.extract_rhi_profile(obj, extracted_obj,
                                                             variables='reflectivity')
    assert np.isclose(np.nansum(extracted_obj['reflectivity'].values), -402880.38)


def test_calc_zdr_offset():
    obj = act.io.armfiles.read_netcdf(radtraq.tests.sample_files.EXAMPLE_XSAPR)
    thresh = {'cross_correlation_ratio_hv': [0.995, 1], 'reflectivity': [10, 30], 'range': [1000, 3000]}
    results = radtraq.proc.calc_zdr_offset(obj, zdr_var='differential_reflectivity', thresh=thresh)
    np.testing.assert_almost_equal(results['bias'], 2.69, decimal=2)
    np.testing.assert_almost_equal(results['profile_reflectivity'][15], 14.37, decimal=2)
