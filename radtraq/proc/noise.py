"""
radtraq.noise
-------------

Module for calculating noise floor and applying a
mask to the data

"""

import dask
import numpy as np
from ..utils.corrections import range_correction


def calc_noise_floor(obj, variable, hvariable):
    """
    Main function for getting the noise floor

    Parameters
    ----------
    obj : xarray object
        ACT object with data
    variable : string
        Variable name to calculate from.  Should be
        a reflectivity
    hvariable : string
        Height variable to use for calculations

    Returns
    -------
    result : list
        Returns the noise floor values for each time sample

    """

    data = obj[variable]
    data = range_correction(data, obj[hvariable])

    n_t, n_h = np.shape(data)

    # noise = np.full(n_t, -100.)
    task = []
    for i in range(n_t):
        task.append(dask.delayed(cloud_threshold)(data[i, :], 1, n_h))
    result = dask.compute(*task)

    return result


def cloud_threshold(data, n_avg, nffts):
    """
    Calculates the noise floor based on code provided to the ARM DQ Office
    by Ieng Jo and Pavlos Kollias while at McGill University

    Parameters
    ----------
    data : xarray DataArray
        xarray data array
    n_avg : float
        Number of points to average over.  Default is normall 1
    nffts : int
        Number of heights to iterate over

    Returns
    -------
    result : list
        Returns the noise floor values for each time sample

    """
    data = 10. ** (data/10.)
    data = np.sort(data)

    nthld = 10. ** -10.
    dsum = 0.
    sumSq = 0.
    n = 0.
    for i in range(nffts):
        if data[i] > nthld:
            dsum += data[i]
            sumSq += data[i] ** 2.0
            n += 1
            a3 = dsum * dsum
            a1 = np.sqrt(n_avg) * (n * sumSq - a3)
            if n > nffts / 4.:
                if a1 <= a3:
                    sumNs = dsum
                    numNs = [n]
                    maxNs = data[i]
            else:
                sumNs = dsum
                numNs = [n]
                maxNs = data[i]

    if len(numNs) > 0:
        n_mean = sumNs / numNs[0]
        n_max = maxNs
        n_points = numNs[0]
    else:
        n_mean = np.nan
        n_max = np.nan
        n_points = np.nan

    return 10. * np.log10(n_mean)
