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
    range_dist_values = slant_range.values.astype(np.float64)
    range_dist_values = range_dist_values * unit_registry.parse_expression(range_units)
    range_dist_values = range_dist_values.to(desired_units).magnitude

    # Calculate height values
    earth_radius = np.array(4. / 3. * 6374., dtype=np.float64)  # Effective earth radius in km.
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


def calculate_azimuth_distance_from_lat_lon(curr_lat=None, curr_lon=None, target_lat=None,
                                            target_lon=None):
    """
    Returns dictionary of distance and direction between two pairs of lat/lon values.

    ...

    Parameters
    ----------
    curr_lat : float
        The latitude of first location assumed to be in same units as target_lat
    curr_lon : float
        The longitude of first location assumed to be in same units as target_lon
    target_lat : float
        The latitude of second location assumed to be in same units as curr_lat
    target_lon : float
        The longitude of second location assumed to be in same units as curr_lon

    Returns
    -------
    dict
        Dictionary containing azimuth and distance from first location to second location.
        Azimiuth values are in degrees and distance is in meters.

    """

    azimuth = np.nan
    distance = np.nan
    doc = {'azimuth': azimuth, 'distance': distance}

    earth_r = 6353000.0
    lon1 = -1.0 * np.radians(curr_lon, dtype=np.float64)
    lat1 = np.radians(curr_lat, dtype=np.float64)
    lon2 = -1.0 * np.radians(target_lon, dtype=np.float64)
    lat2 = np.radians(target_lat, dtype=np.float64)
    delta_lon = lon1 - lon2

    # Calcualte distance
    y = np.sqrt((np.cos(lat2) * np.sin(delta_lon))**2 +
                (np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon))**2)
    x = np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(delta_lon)

    dist_angle = np.arctan2(y, x)
    doc['distance'] = earth_r * dist_angle

    # Calculate azimuth
    y = np.sin(delta_lon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon)

    azimuth = np.degrees(np.arctan2(y, x))
    doc['azimuth'] = np.mod(azimuth, 360.0)

    return doc


def calculate_dual_dop_lobes(coord_dict, min_crossing_angle=20):
    """
    Returns lat/lon of each dual dop lobe at 1 deg resolution

    Parameters
    ----------
    coord_dict : dict
        Dictionary of site coordinates {site: {'lat': 11.11, 'lon': 22.22}}
    min_crossing_angle : float
        Minimum crossing angle for dual doppler

    Returns
    -------
    data : dict
        Dictionary of lat, lon for each lobe

    """
    sites = list(coord_dict.keys())
    theta_r = np.radians(min_crossing_angle)
    data = {}
    ct = 1
    for i in range(len(sites)):
        for j in range(len(sites)):
            if i == j:
                continue
            lon1 = coord_dict[sites[i]]['lon']
            lon2 = coord_dict[sites[j]]['lon']
            lat1 = coord_dict[sites[i]]['lat']
            lat2 = coord_dict[sites[j]]['lat']

            if lon2 > lon1:
                dy = lat2 - lat1
                dx = lon2 - lon1
            else:
                dy = lat1 - lat2
                dx = lon1 - lon2

            phi = np.arctan(dy / dx)

            lon_midpoint = (lon1 + lon2) / 2.
            lat_midpoint = (lat1 + lat2) / 2.
            midpoint = np.sqrt((lon2 - lon1) ** 2. + (lat2 - lat1) ** 2.) / 2.

            h = midpoint / np.tanh(theta_r / 2.)
            h2 = midpoint * np.tanh(theta_r / 2.)
            radius = (h + h2) / 2.

            ycenter = radius - h2
            ycenter2 = -1. * radius + h2

            t = np.arange(-3.5, 3.5, 0.1)
            lobe1_lon = (-1 * ycenter * np.sin(phi)) + lon_midpoint + (radius * np.cos(t))
            lobe1_lat = ycenter * np.cos(phi) + lat_midpoint + (radius * np.sin(t))
            lobe2_lon = ycenter * np.sin(phi) + lon_midpoint + (radius * np.cos(t))
            lobe2_lat = ycenter2 * np.cos(phi) + lat_midpoint + (radius * np.sin(t))

            data['lobe' + str(ct)] = {'lon': lobe1_lon, 'lat': lobe1_lat}
            data['lobe' + str(ct + 1)] = {'lon': lobe2_lon, 'lat': lobe2_lat}
            ct += 2

    return data
