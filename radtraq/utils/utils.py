import pint
import numpy as np
import xarray as xr


def calc_ground_range_and_height(slant_range, elevation):
    """
    Function for calculating height and ground range from a slant range path

    Parameters
    ----------
    slant_range : Xarray.DataArray
        Xarray DataArray containing slant range data including units attribute
    elevation : float
        Elevation angle for slant_range ray in degrees

    Returns
    -------
    obj : Xarray.Dataset
        Xarray Dataset containing 'ground_range' and 'height' DataArrays

    """

    # distance units used in calculations
    desired_units = 'km'
    range_units = slant_range.attrs['units']
    # Convert units to desired_units
    unit_registry = pint.UnitRegistry()
    range_dist_values = slant_range.values
    range_dist_values = range_dist_values * unit_registry.parse_expression(range_units)
    range_dist_values = range_dist_values.to(desired_units).magnitude

    # Calculate height values
    earth_radius = 4. / 3. * 6374.  # Effective earth radius in km.
    height = np.sqrt(earth_radius**2.0 +
                     range_dist_values**2.0 -
                     2.0 * earth_radius * range_dist_values * np.cos(np.deg2rad(elevation + 90.)))

    # Calculate ground range values
    term_1 = earth_radius**2.0 + height**2.0 - range_dist_values**2.0
    term_2 = 2.0 * earth_radius * height
    ground_range = earth_radius * np.arccos(term_1 / term_2)

    # Subtract Earth radius from height
    height = height - earth_radius

    # Convert hieghts back into orginal units
    height = height * unit_registry.parse_expression(desired_units)
    height = height.to(range_units).magnitude

    # Convert ground range into input units
    ground_range = ground_range * unit_registry.parse_expression(desired_units)
    ground_range = ground_range.to(range_units).magnitude

    # Create Dataset to return including attributes.
    return_dataset = xr.Dataset()
    return_dataset['ground_range'] = xr.DataArray(data=ground_range,
                                                  attrs={'long_name': 'Range along ground', 'units': range_units})
    return_dataset['height'] = xr.DataArray(data=height, attrs={'long_name': 'Height above ground',
                                                                'units': range_units, 'standard_name': 'height'})

    return return_dataset
