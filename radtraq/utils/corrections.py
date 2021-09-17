import numpy as np
import pint
import warnings
import xarray as xr

from radtraq.utils.dataset_utils import get_height_variable_name


def range_correction(obj, variable, height_variable=None):
    """
    Corrects reflectivity for range to help get the
    correct noise floor values

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray Dataset containing data
    variable : string
        Varible name to correct
    height_variable : string
        Height varible name to use in correction. If not provided will attempt
        to determine variable name from coordinates on data variable.

    Returns
    -------
    data : Xarray.DataArray
        Returns a range corrected DataArray matching varible name

    """

    if not isinstance(obj, xr.core.dataset.Dataset):
        raise ValueError('Please use a valid Xarray.Dataset')

    if height_variable is None:
        height_variable = get_height_variable_name(obj, variable)

    try:
        height_units = obj[height_variable].attrs['units']
    except KeyError:
        warnings.warn(f"Height variable '{height_variable} does not have units attribute. "
                      "Assuming units are meters.")
        height_units = 'm'

    height = obj[height_variable].values
    desired_unit = 'm'
    if height_units is not desired_unit:
        unit_registry = pint.UnitRegistry()
        height = height * unit_registry.parse_expression(height_units)
        height = height.to(desired_unit)
        height = height.magnitude

    data = obj[variable]

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning,
                                message='.*divide by zero encountered.*')
        data = data - 20. * np.log10(height / 1000.)

    return data
