"""
radtraq.noise
-------------

Module for calculating noise floor and applying a
mask to the data

"""

import dask
import numpy as np
import xarray as xr

from ..utils.corrections import range_correction


def calc_noise_floor(obj, variable, height_variable=None):
    """
    Main function for getting the noise floor

    Parameters
    ----------
    obj : Xarray.dataset
        ACT object with data
    variable : string
        Variable name to calculate. Should be a reflectivity.
    height_variable : string
        Height variable name to use for calculations. If not provided will
        attempt to use coordinates of data variable.

    Returns
    -------
    result : Numpy float array
        Returns the noise floor value for each time sample.

    References
    ----------
    Kollias, P., I. Jo, P. Borque, A. Tatarevic, K. Lamer, N. Bharadwaj, K. Widener,
    K. Johnson, and E.E. Clothiaux, 2014: Scanning ARM Cloud Radars. Part II: Data
    Quality Control and Processing. J. Atmos. Oceanic Technol., 31, 583–598,
    https://doi.org/10.1175/JTECH-D-13-00045.1

    """

    if not isinstance(obj, xr.core.dataset.Dataset):
        raise ValueError('Please use a valid Xarray.Dataset')

    if not isinstance(variable, str):
        raise ValueError('Please Specify a Variable Name')

    # Range correct data and return the DataArray from Dataset
    data = range_correction(obj, variable, height_variable=height_variable)

    # Pass each timestep into task list to calculate cloud threshhold
    # with a delayed dask process
    task = [dask.delayed(cloud_threshold)(row) for row in data]

    # Perform dask computation
    result = dask.compute(*task)

    # Convert returned dask tuple into numpy array
    result = np.array(result, dtype=float)

    return result


def cloud_threshold(data, n_avg=1., nffts=None):
    """
    Calculates the noise floor

    Parameters
    ----------
    data : Xarray.DataArray
        Xarray DataArray
    n_avg : float
        Number of points to average over
    nffts : int
        Number of heights to iterate over. If None will use the size of data.

    Returns
    -------
    result : numpy scalar float
        Returns the noise floor value for each time sample

    References
    ----------
    Kollias, P., I. Jo, P. Borque, A. Tatarevic, K. Lamer, N. Bharadwaj, K. Widener,
    K. Johnson, and E.E. Clothiaux, 2014: Scanning ARM Cloud Radars. Part II: Data
    Quality Control and Processing. J. Atmos. Oceanic Technol., 31, 583–598,
    https://doi.org/10.1175/JTECH-D-13-00045.1

    """

    if nffts is None:
        nffts = data.size

    data = 10. ** (data.values / 10.)
    data = np.sort(data)

    nthld = 10. ** -10.
    dsum = 0.
    sumSq = 0.
    n = 0.
    numNs = []
    sqrt_n_avg = np.sqrt(n_avg)
    for i in range(nffts):
        if data[i] > nthld:
            dsum += data[i]
            sumSq += data[i] ** 2.0
            n += 1.
            a3 = dsum * dsum
            a1 = sqrt_n_avg * (n * sumSq - a3)
            if n > nffts / 4.:
                if a1 <= a3:
                    sumNs = dsum
                    numNs = [n]
            else:
                sumNs = dsum
                numNs = [n]

    if len(numNs) > 0:
        n_mean = sumNs / numNs[0]
    else:
        n_mean = np.nan

    if n_mean == 0.:
        value = np.nan
    else:
        value = 10. * np.log10(n_mean)

    return value
