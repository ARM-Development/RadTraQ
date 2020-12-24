"""
radtraq.proc.profile
--------------------

Module for various processing of profiles
"""
import xarray as xr
import numpy as np


def calc_avg_profile(_obj, variable=None, mask='mask2', mask_val=1, first_height=500.,
                          height='range', ygrid=None):
    """
    Function for calculating average profiles from data after
    applying the cloud mask

    Parameters
    ----------
    _obj : xarray Dataset
        xarray object with all the data
    variable : list
        List of variables to average
    mask : string
        Name of mask in file to apply to data
    mask_val : int
        Value of mask to threshold on
    first_height : float
        First height to start the analysis.  Start at 500 to throw out non-meteorological echo
    height : string
        Name of the height variable to use
    ygrid : numpy array or list
        Numpy array of ygrid values to interpolate to

    Returns
    -------
    _obj : xarray Dataset
        xarray dataset with new variables added

    """

    # Check for variables to process
    if variable is None:
        raise ValueError('Please Specify a Variable Name')

    # Check for first_height, if none is passed used first in data
    if first_height is None:
        first_height = _obj[height].values[0]

    # If ygrid is not passed, set one up
    if ygrid is None:
        ygrid = np.arange(first_height, 15000, 50)

    # Get height attributes as they do disappear at some point
    ht_attrs = _obj[height].attrs

    # Interpolate the data to height grid
    # Note, standard methodology dictates that logarithmic data
    # should be converted to linear space before averaging
    # This will need to be added in the future
    _obj = _obj.interp(coords={height: ygrid}, method='nearest')

    # Apply mask to data
    obj = _obj
    obj = obj.where(obj[mask] == mask_val)

    # Mask data based on first_height to use
    obj = obj.where(obj[height] >= first_height)

    # For each variable, calculate average profile
    # and add back into the dataset
    prof_names = []
    for var in variable:
        prof = obj[var].mean(axis=0, skipna=True)

        # Add data back to the object
        prof_name = var+'_avg_prof'
        prof_names.append(prof_name)
        long_name = 'Average profile of '+var
        attrs = {'long_name': long_name, 'units': obj[var].attrs['units']}
        da = xr.DataArray(prof.values, dims=[height], coords=[obj[height].values], attrs=attrs)
        _obj[prof_name] = da

    _obj.attrs['_prof_names'] = prof_names

    obj.close()

    _obj[height].attrs = ht_attrs

    return _obj
