"""
radtraq.plotting.cfad
---------------------

Module for calculating and plotting a cfad using
an act object as input

"""

import dask
import numpy as np
import warnings
import matplotlib.pyplot as plt
import xarray as xr

from radtraq.utils.dataset_utils import get_height_variable_name


def plot_cfad(hist, x, y):
    """
    Function for plotting up CFAD given 2D histogram, x, and y

    Parameters
    ----------
    hist : list
        2D list of histogram data from calc_cfad
    x : list
        List of x values
    y : list
        List of y values

    Returns
    -------
    fig : matplotlib ax handle
        Returns the axis handle for additional updates if needed

    """

    fig, ax = plt.subplots()
    cs = ax.contourf(x, y, hist, 50)
    fig.colorbar(cs)

    return ax


def calc_cfad(obj, variable, height_variable=None, xbins=None):
    """
    Function for calculating CFAD

    Parameters
    ----------
    object : Xarray.Dataset
        ACT object containing vertical point data
    variable : string
        Variable to calculate CFAD
    height_variable : string
        Name of the height variable to use. If set to None, will attempt to determine
        by using coordinate varible name.
    xbins : list
        List of bins to calculate CFAD. If None will calcualte a default.

    Returns
    -------
    data_array : Xarray.DataArray
        DataArray containg results from CFAD analysis and coordinate variables

    """
    # Determine height coordinate varible name.
    if height_variable is None:
        height_variable = get_height_variable_name(obj, variable)

    data = obj[variable]
    height = obj[height_variable]

    if xbins is None:
        xbins = np.linspace(-70, 50, 121)

    dsk = []
    for j in range(len(height)):
        a = dask.delayed(np.histogram)(data[:, j], bins=xbins)
        dsk.append(a[0])

    hist = dask.compute(*dsk)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning,
                                message='.*divide by zero encountered in log10.*')
        hist = np.log10(np.array(hist))

    coords = {'x': xbins[:-1], height_variable: height}
    dims = [height_variable, "x"]
    attrs = {'long_name': f'CFAD for {variable}', 'units': '1'}

    data_array = xr.DataArray(data=hist, dims=dims, coords=coords, attrs=attrs)
    data_array['x'].attrs = {'long_name': 'X bins for CFAD', 'units': '1'}

    return data_array
