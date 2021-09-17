import xarray as xr


def get_height_variable_name(obj, variable=None):
    """
    Determines the height variable name in the Dataset using variable
    coordinate information.

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray Dataset containing data
    variable : string
        Varible name to correct

    Returns
    -------
    height_variable : string
        Height variable name

    """
    if not isinstance(obj, xr.core.dataset.Dataset):
        raise ValueError('Please use a valid Xarray.Dataset')

    if not isinstance(variable, str):
        raise ValueError('Please Specify a Variable Name')

    height_variable = None

    # Determine height coordinate varible name.
    dims = obj[variable].dims

    if len(dims) == 2:
        height_variable = list(set(dims) - set(['time']))
        if len(height_variable) == 1:
            height_variable = height_variable[0]

    if height_variable is None:
        raise RuntimeError(f"Unable to determine height variable name for {variable}.")

    return height_variable
