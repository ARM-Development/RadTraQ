import numpy as np


def range_correction(data, height):
    """
    Corrects reflectivity for range to help get the
    correct noise floor values

    Parameters
    ----------
    data : xarray DataArray
        xarray data array
    height : xarray DataArray
        Heights over which to correct the data for

    Returns
    -------
    data : list
        Returns a range corrected variable

    """
    data = data - 20. * np.log10(height/1000.)

    return data
