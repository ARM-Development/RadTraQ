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


def calc_cloud_mask(obj, variable, height_variable=None, noise_threshold=-45.,
                    threshold_offset=5., counts_threshold=12):
    """
    Main function for calculating the cloud mask

    Parameters
    ----------
    obj : Xarray.dataset
        ACT object with data
    variable : string
        Variable name to calculate. Should be a reflectivity.
    height_variable : string
        Height variable name to use for calculations. If not provided will
        attempt to use coordinates of data variable.
    noise_threshold : float
        Threshold value used for noise detection. Greater than this value.
    threshold_offset : float
        Threshold offset value used for noise detection
    counts_threshold : int
        Threshold of counts used to determine mask. Greater than or equal to this value.


    Returns
    -------
    result : Xarray.dataset
        Returns the updated dataset with noise floor masks added for each time samplea

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

    noise = calc_noise_floor(obj, variable, height_variable)

    noise_thresh = np.nanmin(np.vstack([noise, np.full(np.shape(obj[variable])[0],
                             noise_threshold)]), axis=0) + threshold_offset

    data = range_correction(obj, variable, height_variable=height_variable)

    task = []
    for i in range(np.shape(data)[0]):
        task.append(dask.delayed(first_mask)(data[i, :], noise_thresh[i]))

    result = dask.compute(task)
    mask1 = np.array(result[0])

    counts = signal.convolve2d(mask1, np.ones((4, 4), dtype=int), mode='same')
    mask2 = np.zeros_like(data, dtype=np.int16)
    mask2[counts >= counts_threshold] = 1

    # Convert masks from numpy arrays to dask arrays, matching the chunksize
    # of data in Xarray dataset.
    mask1 = dask.array.from_array(mask1, chunks=obj[variable].data.chunksize)
    mask2 = dask.array.from_array(mask2, chunks=obj[variable].data.chunksize)

    # Add masks to dataset
    coords = obj[variable].coords
    obj['cloud_mask_1'] = xr.DataArray(
        mask1, coords=coords,
        attrs={'long_name': 'Cloud mask 1 (linear profile)',
               'units': '1',
               'comment': 'The mask is calculated with a '
               'linear mask along each time profile.',
               'flag_values': [0, 1], 'flag_meanings': ['no_cloud', 'cloud'],
               'variable_used': variable})
    obj['cloud_mask_2'] = xr.DataArray(
        mask2, coords=coords,
        attrs={'long_name': 'Cloud mask 2 (2D box)', 'units': '1',
               'comment': 'The mask uses a 2D box to '
               'filter out noise.', 'flag_values': [0, 1],
               'flag_meanings': ['no_cloud', 'cloud'],
               'variable_used': variable})

    return obj


def first_mask(data, noise_threshold):
    mask = np.zeros_like(data, dtype=np.int16)
    mask[data > noise_threshold] = 1

    return mask
