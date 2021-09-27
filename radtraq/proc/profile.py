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
from radtraq.utils.utils import calc_ground_range_and_height, calculate_azimuth_distance_from_lat_lon


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


def extract_profile(obj, azimuth, ground_dist, variables=None, azimuth_range=None,
                    ground_dist_range=200, azimuth_name='azimuth', range_name='range',
                    ground_range_units='m', elevation_name="elevation"):

    """
    Function for extracting vertical profile over a location from a PPI scan
    giving azimuth direction and ground range distance

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray object with all the data
    azimuth : float
        Azimuth direction to extract profile in degrees
    ground_dist : float
        Horizontal ground distance to extract profile
    variables : str, list, None
        List of variables to extract profile
    azimuth_range : float, None
        Range to use for tollerance in selecting azimuth to extract profile. If set to None
        will use the mode of azimuth differences. Assumed to be in degrees.
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

    # If no variable names provided get list of names by checking dimentions.
    if variables is None:
        variables = []
        for var_name in list(obj.keys()):
            if (len(obj[var_name].dims) == 2 and
                    len(set(obj[var_name].dims) - set(['time', range_name])) == 0):
                variables.append(var_name)

    if isinstance(variables, str):
        variables = [variables]

    unit_registry = pint.UnitRegistry()

    azimuth_da = obj[azimuth_name]
    azimuth_values = azimuth_da.values
    azimuth_values = azimuth_values * unit_registry.parse_expression(azimuth_da.attrs['units'])
    azimuth_values = azimuth_values.to('degree').magnitude
    azimuth_da.values = azimuth_values
    azimuth_da.attrs['units'] = 'degree'
    if azimuth_range is None:
        azimuth_range = np.floor(np.abs(np.diff(azimuth_da.values)))
        azimuth_range = stats.mode(azimuth_range).mode[0]

    azimuth_index = np.argmin(np.abs(azimuth_da.values - azimuth))
    azimuth_value = azimuth_da.values[azimuth_index]

    # Check if azimuth and range match in PPI scan. If not return None
    if not (np.abs(azimuth - azimuth_value)) <= (azimuth_range / 2.):
        return profile_obj

    temp_obj = obj.where((azimuth_da >= (azimuth_value - azimuth_range / 2.)) &
                         (azimuth_da <= (azimuth_value + azimuth_range / 2.)), drop=True)

    range_index = []
    height = []
    elevation = temp_obj[elevation_name].values
    elevation = elevation * unit_registry.parse_expression(obj[elevation_name].attrs['units'])
    elevation = elevation.to('degree').magnitude

    ground_dist = ground_dist * unit_registry.parse_expression(ground_range_units)
    ground_dist = ground_dist.to(temp_obj[range_name].attrs['units']).magnitude

    ground_dist_range = ground_dist_range * unit_registry.parse_expression(ground_range_units)
    ground_dist_range = ground_dist_range.to(temp_obj[range_name].attrs['units']).magnitude

    true_range = None
    for elev in elevation:
        result = calc_ground_range_and_height(temp_obj[range_name], elev)
        index = np.nanargmin(np.abs(result['ground_range'].values - ground_dist))
        if true_range is None:
            true_range = result['ground_range'].values[index]

        range_index.append(index)
        height.append(result['height'].values[index])

    if not np.abs(ground_dist - true_range) <= ground_dist_range:
        return profile_obj

    profile_obj = xr.Dataset()
    profile_obj['time'] = temp_obj['time']
    profile_obj = profile_obj.assign_coords(height=height)
    profile_obj['height'].attrs = {'long_name': 'Height above ground',
                                   'units': temp_obj[range_name].attrs['units'],
                                   'standard_name': 'height'}

    for var_name in variables:
        data = temp_obj[var_name].values[:, range_index]
        profile_obj[var_name] = xr.DataArray(data=data, dims=['time', 'height'],
                                             attrs=temp_obj[var_name].attrs)

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
    result = destination_azimuth_distance(lat_value, lon_value, azimuth_value, true_range,
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
    del profile_obj[elevation_name]
    del profile_obj[azimuth_name]

    return profile_obj


def extract_profile_at_lat_lon(obj, desired_lat, desired_lon, azimuth_name='azimuth',
                               range_name='range', elevation_name="elevation", azimuth_range=None,
                               variables=None, lat_name_in_obj='lat', lon_name_in_obj='lon',):

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
    azimuth_name : str
        Name of azimuth variable in obj
    range_name : str
        Name of range variable in obj
    elevation_name : str
        Name of elevation variable in obj
    azimuth_range : float or None
        Range to use for tollerance in selecting azimuth to extract profile. If set to None
        will use the mode of azimuth differences. Assumed to be in degrees.
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

    profile_obj = extract_profile(obj, result['azimuth'], result['distance'], variables=variables,
                                  azimuth_range=azimuth_range, azimuth_name=azimuth_name,
                                  range_name=range_name, ground_range_units='m',
                                  elevation_name=elevation_name)

    return profile_obj
