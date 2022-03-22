"""
radtraq.proc.profile
--------------------

Module for various processing of profiles
"""
import xarray as xr
import numpy as np
import warnings
import pint
from scipy import stats
from act.utils.geo_utils import destination_azimuth_distance

from radtraq.proc.cloud_mask import calc_cloud_mask
from radtraq.utils.dataset_utils import get_height_variable_name
from radtraq.utils.utils import (calc_ground_range_and_height,
                                 calculate_azimuth_distance_from_lat_lon)


def calc_avg_profile(_obj, variable=None, mask_variable='cloud_mask_2',
                     mask_value=None, mask_meaning='cloud', first_height=500.,
                     last_height=15000., step_height=50,
                     height_variable=None, ygrid=None):
    """
    Function for calculating average profiles from data after
    applying the cloud mask

    Parameters
    ----------
    _obj : Xarray.Dataset
        xarray object with all the data
    variable : str or list
        List of variables to average
    mask_variable : string
        Name of mask variable to apply to data
    mask_value : int
        Value of mask to filter
    mask_meaning : string
        Mask meaning listed in mask variable flag_meanings. Ignored if mask_value set.
    first_height : float
        First height to start the analysis. Start at 500 to throw out non-meteorological echo
    last_height : float
        Last height to end the analysis.
    step_height : float
        Height step value to use between first_height and last_height to make ygrid.
    height_variable : string
        Name of the height variable to use. If set to None, will attempt to determine
        by using coordinate varible name.
    ygrid : numpy array or list
        Numpy array of ygrid values to interpolate. first_height, last_height, step_height
        ignored if set.

    Returns
    -------
    obj : Xarray.Dataset
        xarray dataset with new variables added

    References
    ----------
    Kollias, P., I. Jo, P. Borque, A. Tatarevic, K. Lamer, N. Bharadwaj, K. Widener,
    K. Johnson, and E.E. Clothiaux, 2014: Scanning ARM Cloud Radars. Part II: Data
    Quality Control and Processing. J. Atmos. Oceanic Technol., 31, 583–598,
    https://doi.org/10.1175/JTECH-D-13-00045.1

    """

    # Check for variables to process
    if variable is None:
        raise ValueError('Please Specify a Variable Name')

    if isinstance(variable, str):
        variable = [variable]

    # Determine height coordinate varible name.
    if height_variable is None:
        height_variable = get_height_variable_name(_obj, variable[0])

    # Check for first_height, if none is passed used first in data
    if first_height is None:
        first_height = _obj[height_variable].values[0]

    # If ygrid is not passed, set one up
    if ygrid is None:
        ygrid = np.arange(first_height, last_height, step_height)

    # Get height attributes as they do disappear at some point
    ht_attrs = _obj[height_variable].attrs

    # Get variable name for calc_cloud_mask
    if mask_variable in _obj.keys():
        try:
            cloud_mask_variable_name = _obj[mask_variable].attrs['variable_used']
        except KeyError:
            cloud_mask_variable_name = variable[0]
    else:
        cloud_mask_variable_name = variable[0]

    # Get data types for all variables to double check later on if the int
    # type were up converted to float.
    dtypes = {var_name: _obj[var_name].dtype for var_name in _obj.keys()}

    # Interpolate the data to height grid
    # Note, standard methodology dictates that logarithmic data
    # should be converted to linear space before averaging
    # This will need to be added in the future
    obj = _obj.interp(coords={height_variable: ygrid}, method='nearest')

    # The interp method will convert the mask values to float and interpret.
    # So we need to correct the data type of the mask and add missing meaning.
    if mask_variable not in list(obj.keys()):
        obj = calc_cloud_mask(obj, cloud_mask_variable_name, height_variable=height_variable)

        # Add new variables to dtypes dictionary
        for var_name in list(obj.keys()):
            if var_name in list(dtypes.keys()):
                continue
            dtypes[var_name] = obj[var_name].dtype

    # Apply mask to data
    if mask_value is None:
        flag_values = obj[mask_variable].attrs['flag_values']
        flag_meanings = obj[mask_variable].attrs['flag_meanings']
        index = flag_meanings.index(mask_meaning)
        mask_value = flag_values[index]

    obj = obj.where(obj[mask_variable] == mask_value)

    # Mask data based on first_height to use
    obj = obj.where(obj[height_variable] >= first_height)

    # For each variable, calculate average profile and add back into the dataset
    prof_names = []
    for var in variable:
        prof = obj[var].mean(axis=0, skipna=True)

        # Add data back to the object
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning,
                                    message='.*invalid value encountered in true_divide.*')
            prof_name = var + '_avg_prof'
            prof_names.append(prof_name)
            long_name = 'Average profile of ' + var
            attrs = {'long_name': long_name, 'units': obj[var].attrs['units']}
            da = xr.DataArray(prof.values, dims=[height_variable],
                              coords=[obj[height_variable].values], attrs=attrs)
            obj[prof_name] = da

    obj.attrs['_prof_names'] = prof_names

    # Fix height variable attributes
    obj[height_variable].attrs = ht_attrs

    # The data type of mask variables is changed in this process. Change the
    # mask from float to inteter.
    for var_name, dtype in dtypes.items():
        try:
            if obj[var_name].dtype == dtype:
                continue

            flag_values = obj[var_name].attrs['flag_values']
            flag_meanings = obj[var_name].attrs['flag_meanings']
            index = 0
            for ii in ['missing', 'no_cloud']:
                try:
                    index = flag_meanings.index(ii)
                    break
                except ValueError:
                    pass

            data = obj[var_name].values
            data[np.isnan(data)] = flag_values[index]
            obj[var_name].values = data
            obj[var_name] = obj[var_name].astype(dtype)
        except KeyError:
            pass

    return obj


def extract_profile(obj, azimuth, ground_dist, append_obj=None, variables=None,
                    azimuth_range=None, ground_dist_range=200, azimuth_name='azimuth',
                    range_name='range', ground_range_units='m', elevation_name="elevation"):

    """
    Function for extracting vertical profile over a location from a PPI scan
    giving azimuth direction and ground range distance

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray Dataset with all the data
    azimuth : float
        Azimuth direction to extract profile in degrees
    ground_dist : float
        Horizontal ground distance to extract profile
    append_obj : Xarray.Dataset
        Xarray Dataset to return with new profile appened.
    variables : str, list, None
        List of variables to extract profile
    azimuth_range : float, None
        Range to used to determine if close to correct profile location. If set to None will
        calculate using mode of difference. Assumed to be in degrees.
    ground_dist_range : float
        Distance range window size allowed to extract profile. If the profile location is
        off from lat/lon location by more than this distance, will not extract a profile
        and will return None.
    azimuth_name : string
        Variable name in Xarray object containing azimuth values.
    range_name : string
        Variable name in Xarray object containing range values.
    ground_range_units : string
        ground_dist units
    elevation_name : string
        Variable name in Xarray object containing elevation values. Assumed to be in degrees.

    Returns
    -------
    obj : Xarray.Dataset or None
        Xarray Dataset with profile extracted and new coordinate variable height added
        or if unable to find profile returns None.

    """

    profile_obj = None
    if append_obj is not None:
        profile_obj = append_obj

    # If no variable names provided get list of names by checking dimentions.
    if variables is None:
        variables = []
        for var_name in list(obj.keys()):
            if (len(obj[var_name].dims) == 2 and
                    len(set(obj[var_name].dims) - set(['time', range_name])) == 0):
                variables.append(var_name)

    elif isinstance(variables, str):
        variables = [variables]

    unit_registry = pint.UnitRegistry()

    if azimuth_range is None:
        azimuth_range = np.floor(np.abs(np.diff(obj[azimuth_name].values)))
        azimuth_range = stats.mode(azimuth_range).mode[0]

    ground_dist = ground_dist * unit_registry.parse_expression(ground_range_units)
    ground_dist = ground_dist.to(obj[range_name].attrs['units']).magnitude

    ground_dist_range = ground_dist_range * unit_registry.parse_expression(ground_range_units)
    ground_dist_range = ground_dist_range.to(obj[range_name].attrs['units']).magnitude

    number_of_sweeps = obj['sweep_start_ray_index'].values.size
    height = np.empty(number_of_sweeps, dtype=np.float32)
    found_value = np.full(number_of_sweeps, False)
    range_index = []
    time_index = []
    true_range = None
    true_azimuth = None

    for sweep_number in range(0, number_of_sweeps):
        index = np.arange(obj['sweep_start_ray_index'].values[sweep_number],
                          obj['sweep_end_ray_index'].values[sweep_number] + 1, dtype=int)

        index = index[0] + np.argmin(np.abs(obj[azimuth_name].values[index] - azimuth))
        matched_azimuth = obj[azimuth_name].values[index]
        matched_elevation = obj[elevation_name].values[index]

        result = calc_ground_range_and_height(obj[range_name], matched_elevation)
        rng_index = np.nanargmin(np.abs(result['ground_range'].values - ground_dist))
        if true_range is None:
            true_range = result['ground_range'].values[rng_index]

        range_index.append(rng_index)
        height[sweep_number] = result['height'].values[rng_index]
        time_index.append(index)

        if np.abs(matched_azimuth - azimuth) <= azimuth_range:
            found_value[sweep_number] = True

            if true_azimuth is None:
                true_azimuth = matched_azimuth

    # Check if azimuth values are within range
    if not np.all(found_value):
        return profile_obj

    # Check if the distance is within range
    if not np.abs(ground_dist - true_range) <= ground_dist_range:
        return profile_obj

    temp_obj = obj.isel(time=time_index)
    write_time = [temp_obj['time'].values[0] + (temp_obj['time'].values[-1] - temp_obj['time'].values[0]) / 2]

    profile_obj = xr.Dataset()
    profile_obj = profile_obj.assign_coords(time=write_time)
    profile_obj = profile_obj.assign_coords(height=height)

    for var_name in variables:
        data = np.full((1, len(range_index)), np.nan)
        for ii, _ in enumerate(range_index):
            if not found_value[sweep_number]:
                continue

            data[0, ii] = temp_obj[var_name].values[ii, range_index[ii]]

        profile_obj[var_name] = xr.DataArray(data=data, dims=['time', 'height'],
                                             attrs=obj[var_name].attrs)

    # Adding attributes for coordinate variables after subsetting data because
    # setting values to DataArray with dims defined clears the attributes.
    profile_obj['time'].attrs = temp_obj['time'].attrs
    profile_obj['height'].attrs = {'long_name': 'Height above ground',
                                   'units': temp_obj[range_name].attrs['units'],
                                   'standard_name': 'height'}

    # Add location variables
    # Get latitude variable name
    lat_name = ''
    for var_name in ['lat', 'latitude']:
        try:
            temp_obj[var_name]
            lat_name = var_name
            break
        except KeyError:
            pass

    # Get longitude variable name
    lon_name = ''
    for var_name in ['lon', 'longitude']:
        try:
            temp_obj[var_name]
            lon_name = var_name
            break
        except KeyError:
            pass

    # Get altitude variable name
    alt_name = ''
    for var_name in ['alt', 'altitude']:
        try:
            temp_obj[var_name]
            alt_name = var_name
            break
        except KeyError:
            pass

    # Get location variables and ensure scalar value
    lat_value = temp_obj[lat_name].values
    lon_value = temp_obj[lon_name].values
    if len(lat_value.shape) > 0:
        lat_value = lat_value[0]
    if len(lon_value.shape) > 0:
        lon_value = lon_value[0]

    # Calcualte new lat/lon values from radar location and azimuth and range
    result = destination_azimuth_distance(lat_value, lon_value, true_azimuth, true_range,
                                          dist_units=temp_obj[range_name].attrs['units'])

    # Copy over DataArray for attributes
    profile_obj[lat_name] = temp_obj[lat_name]
    profile_obj[lon_name] = temp_obj[lon_name]
    profile_obj[alt_name] = temp_obj[alt_name]

    # Replace latitude values with calculated value
    if len(profile_obj[lat_name].values.shape) > 0:
        profile_obj[lat_name].values = np.full(profile_obj[lat_name].values.shape, result[0])
    else:
        profile_obj[lat_name].values = result[0]

    # Replace longitude values with calculated value
    if len(profile_obj[lon_name].values.shape) > 0:
        profile_obj[lon_name].values = np.full(profile_obj[lon_name].values.shape, result[1])
    else:
        profile_obj[lon_name].values = result[1]

    del temp_obj

    if isinstance(append_obj, xr.core.dataset.Dataset):
        profile_obj = xr.concat([append_obj, profile_obj], dim='time')

    return profile_obj


def extract_profile_at_lat_lon(obj, desired_lat, desired_lon, append_obj=None, azimuth_name='azimuth',
                               range_name='range', elevation_name="elevation", azimuth_range=None,
                               ground_dist_range=200, variables=None, lat_name_in_obj='lat',
                               lon_name_in_obj='lon'):

    """
    Function for extracting vertical profile over a location defined by latitude
    and longitude from a PPI scan

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray object with all the data
    desired_lat : float
        Latitude of desired profile in same units as latitued in obj
    desired_lon : float
        Longitude of desired profile in same units as longitude in obj
    append_obj : Xarray.Dataset
        Xarray Dataset to return with new profile appened.
    azimuth_name : str
        Name of azimuth variable in obj
    range_name : str
        Name of range variable in obj
    elevation_name : str
        Name of elevation variable in obj
    azimuth_range : float or None
        Range to use for tollerance in selecting azimuth to extract profile. If set to None
        will use the mode of azimuth differences. Assumed to be in degrees.
    ground_dist_range : float
        Distance range window size allowed to extract profile. If the profile location is
        off from lat/lon location by more than this distance, will not extract a profile
        and will return None.
    variables : str, list, None
        List of variables to extract profile
    lat_name_in_obj : str
        Name of latitude varible in object
    lon_name_in_obj : str
        Name of longitude varible in object

    Returns
    -------
    obj : Xarray.Dataset
        Xarray Dataset with profile extracted at desired latitued and longitude location,
        and new coordinate variable height added.

    """

    lat = obj[lat_name_in_obj].values
    lon = obj[lon_name_in_obj].values
    if len(lat.shape) > 0:
        lat = lat[0]
    if len(lon.shape) > 0:
        lon = lon[0]

    result = calculate_azimuth_distance_from_lat_lon(lat, lon, desired_lat, desired_lon)

    profile_obj = extract_profile(obj, result['azimuth'], result['distance'],
                                  append_obj=append_obj, variables=variables,
                                  azimuth_range=azimuth_range, azimuth_name=azimuth_name,
                                  range_name=range_name, ground_range_units='m',
                                  elevation_name=elevation_name,
                                  ground_dist_range=ground_dist_range)

    return profile_obj


def extract_rhi_profile(obj, append_obj=None, variables=None,
                        elevation_range=[89, 91], elevation_name="elevation",
                        sweep_variables=['sweep_start_ray_index', 'sweep_end_ray_index']):
    """
    Function for extracting vertical profile over a location from a RHI scan

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray object with all the data. Requires the additional variables in sweep_variables
        for finding sweeps. They will be removed from returned Dataset to allow concatination.
    append_obj : Xarray.Dataset
        If provided will append extracted profiles to this object.
    variables : str, list, None
        List of variables to return in extracted Dataset. If set to None returns all variables
        in the Dataset.
    elevation_range : list
        Range of elevation values to use in subsetting to find a vertical profile. Will return
        profile closest to 90 degrees for each RHI scan that fits within this range. If the
        scan does not have a value within this range, will skip that scan. Assumed to be in degrees.
    elevation_name : string
        Variable name in Xarray object containing elevation values. Assumed to be in degrees.
    sweep_variables : list of str
        Variable names used to determine sweeps to extract profile.

    Returns
    -------
    obj : Xarray.Dataset or None
        Xarray Dataset with profile extracted and new coordinate variable height added
        or if unable to find profile returns None.

    """
    if obj is None:
        return append_obj

    extract_index = []
    for ii, _ in enumerate(obj[sweep_variables[0]].values):
        index = np.arange(obj[sweep_variables[0]].values[ii],
                          obj[sweep_variables[1]].values[ii], dtype=int)

        index = index[0] + np.argmin(np.abs(obj[elevation_name].values[index] - 90.))
        elevation = obj[elevation_name].values[index]
        if elevation >= elevation_range[0] and elevation <= elevation_range[1]:
            extract_index.append(index)

    if len(extract_index) > 0:
        obj = obj.isel(time=extract_index)

        for var_name in sweep_variables:
            del obj[var_name]

        if variables is not None:
            if isinstance(variables, str):
                variables = [variables]

            obj = obj[variables]

        if isinstance(append_obj, xr.core.dataset.Dataset):
            append_obj = xr.concat([append_obj, obj], dim='time')
        else:
            append_obj = obj

    return append_obj


def calc_zdr_offset(obj, zdr_var=None, thresh=None):
    """
    Function for extracting vertical profile over a location from a RHI scan

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray object with radar data
    zdr_var : string
        Variable name for differential reflectivity
    thresh : dict
        Disctionary of variables and values following the form of
        thresh = {'cross_correlation_ratio_hv': [0.995, 1], 'reflectivity': [10, 30], 'range': [1000, 3000]}

    Returns
    -------
    obj : Xarray.Dataset or None
        Xarray Dataset with profile extracted and new coordinate variable height added
        or if unable to find profile returns None.

    """
    height_var = get_height_variable_name(obj, variable=zdr_var)
    new = obj
    for k in thresh:
        new = new.where(obj[k] >= thresh[k][0])
        new = new.where(obj[k] <= thresh[k][1])
    bias = np.nanmean(new[zdr_var].values)

    results = {'bias': bias, 'profile_zdr': new[zdr_var].mean(dim='time').values,
               'range': new[height_var].values}
    for k in thresh:
        if k != height_var:
            results['profile_' + k] = new[k].mean(dim='time').values

    return results
