"""
radtraq.plotting.self_consistency
---------------------

Module for plotting self-consistency histograms

"""


import numpy as np
import matplotlib.pyplot as plt
import scipy

from radtraq.utils.dataset_utils import get_height_variable_name


def plot_self_consistency(obj, variables=None, thresh=None):
    """
    Function for plotting self-consistency plots

    Parameters
    ----------
    object : Xarray.Dataset
        ACT object containing vertical point data
    variables : dict
        Dictionary of variables to plot with format of
        {yvariable: {'variable': x-variable, 'bin_width': [1, 2], 'linreg': True}}
    thresh : dict
        dictionary of variables to threshold the data from.  For example
        thresh = {'copol_correlation_coeff': 0.99}

    Returns
    -------
    ax : matplotlib ax handle
        Returns the axis handle for additional updates if needed

    """

    if thresh is not None:
        thresh_vars = list(thresh.keys())
    comp_vars = [variables[k]['variable'] for k in variables.keys()]
    var = list(variables.keys()) + thresh_vars + comp_vars

    # Threshold all variables based on thresh
    new_obj = obj[var]
    height_var = get_height_variable_name(new_obj, variable=var[0])
    new_obj = new_obj.stack(z=('time', height_var))
    new_obj = new_obj.dropna(dim='z')
    if thresh is not None:
        for k in thresh:
            new_obj = new_obj.where(new_obj[k] > thresh[k], drop=True)

    # Set up plots
    n_plots = len(variables.keys())
    nc = 2
    nr = int(np.ceil(n_plots / 2.))
    fig, ax = plt.subplots(nc, nr, figsize=(5 * nr, 4.25 * nc))

    # Cycle through each plot and create comparison
    i = 0
    j = 0
    for k in variables:
        bin_width = [1, 1]
        if 'bin_width' in variables[k]:
            bin_width = variables[k]['bin_width']
        comp_var = variables[k]['variable']
        xbins = int((new_obj[comp_var].max() - new_obj[comp_var].min()) / bin_width[0])
        ybins = int((new_obj[k].max() - new_obj[k].min()) / bin_width[1])
        ax[i, j].hist2d(new_obj[comp_var], new_obj[k], bins=[xbins, ybins], cmin=1)

        ax[i, j].set_xlabel(new_obj[comp_var].attrs['long_name'])
        ax[i, j].set_ylabel(new_obj[k].attrs['long_name'])
        ax[i, j].set_title(new_obj[k].attrs['long_name'].split(',')[0] + ' vs \n' +
                           new_obj[comp_var].attrs['long_name'])
        if 'linreg' in variables[k]:
            results = scipy.stats.linregress(new_obj[comp_var], new_obj[k])
            text = '%.2f' % results.intercept + ' + ' + '%.2f' % results.slope + 'x'
            ax[0, 0].text(new_obj[comp_var].max(), new_obj[k].max(), text, ha='right', va='top')
            ax[0, 0].plot(new_obj[comp_var].values, new_obj[comp_var].values * results.slope +
                          results.intercept, 'r')

        j += 1
        if j >= nc:
            j = 0
            i += 1

    plt.tight_layout()
    return ax
