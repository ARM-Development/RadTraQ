"""
radtraq.cloud_mask
------------------

Module for calculating cloud masks based off of the
noise floor calculations in radtraq.noise

"""

import dask
import numpy as np
import xarray as xr
from scipy import signal
from .noise import calc_noise_floor
from ..utils.corrections import range_correction


def calc_cloud_mask(obj, variable, hvariable, noise_threshold=-45.,
                    threshold_offset=5.):
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

    noise = calc_noise_floor(obj, variable, hvariable)

    # mask = np.full(np.shape(obj[variable]), 0)
    mask2 = np.full(np.shape(obj[variable]), 0)
    noise_thresh = np.nanmin(np.vstack([noise, np.full(np.shape(obj[variable])[0],
                             noise_threshold)]), axis=0) + threshold_offset

    data = range_correction(obj[variable].values, obj[hvariable].values)
    task = []
    for i in range(np.shape(data)[0]):
        task.append(dask.delayed(first_mask)(data[i, :], noise_thresh[i]))

    result = dask.compute(task)
    mask1 = [list(r) for r in result[0]]

    counts = signal.convolve2d(mask1, np.ones((4, 4)), mode='same')
    index = np.where(counts >= 12)
    mask2 = np.zeros(np.shape(data))
    mask2[index] = 1.

    coords = obj[variable].coords
    obj['mask1'] = xr.DataArray(mask1, coords=coords)
    obj['mask2'] = xr.DataArray(mask2, coords=coords)

    return obj


def first_mask(data, noise_threshold):
    index = np.where(data > noise_threshold)
    mask = np.zeros(np.shape(data)[0])
    mask[index] = 1

    return mask
