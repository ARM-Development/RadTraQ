"""
radtraq.plotting.cfad
---------------------

Module for calculating and plotting a cfad using
an act object as input

"""

import dask
import numpy as np
import matplotlib.pyplot as plt


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


def calc_cfad(obj, variable, hvariable, xbins=None):
    """
    Function for plotting up CFAD given 2D histogram, x, and y

    Parameters
    ----------
    object : xarray Dataset
        ACT object containing vertical point data
    variable : string
        Variable to calculate CFAD for
    hvariable : string
        Variable name for the height data
    xbins : list
        List of bins to calculate cfad for

    Returns
    -------
    hist : list
        2D List of histogram results
    xbins : list
        List of xbins that were used
    height : list
        List of heights from the hvariable

    """
    data = obj[variable]
    height = obj[hvariable]

    if xbins is None:
        xbins = np.linspace(-70, 50, 121)

    dsk = []
    for j in range(len(height)):
        a = dask.delayed(np.histogram)(data[:, j], bins=xbins)
        dsk.append(a)

    hist = dask.compute(*dsk)

    hist = [np.log10(h[0]) for h in hist]

    return hist, xbins[:-1], height
