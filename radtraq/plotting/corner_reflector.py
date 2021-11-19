import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import pandas as pd
import copy


def plot_cr_raster(obj, field='reflectivity', target_range=None, ax=None, fig=None,
                   delta_x=None, delta_y=None, target_limits=None, az_limits=None,
                   el_limits=None, vmin=None, vmax=None, cmap=None, title=None,
                   title_flag=True, axislabels=[None, None], axislabels_flag=True,
                   colorbar_flag=True, colorbar_label=None, colorbar_orient='vertical',
                   noplot=False, az_field='azimuth', el_field='elevation', range_field='range'):
    """
    Plot a corner reflector raster scan

    Parameters
    ----------
    obj : Xarray.Dataset
        Xarray Dataset containing data
    field : String
        Field to plot if other than reflectivity
    target_range : Float
        Estimated range of the corner reflector
    ax : Axis
        Axis to plot on. None will use the current axis.
    fig : Figure
        Figure to add the colorbar to. None will use the current figure.
    delta_x : Float
        Azimuth grid spacing for griddata
    delta_y : Float
        Elevation grid spacing for griddata
    target_limits : list
        Distance limits in form [min, max] used to subset the data when determining
        what range to analyze. This is ignored if target_range is set.
    az_limits : list
        Azimuth limits in form [min, max]
    el_limits : list
        Elevation limits in form [min, max]
    vmin : float
        Luminance minimum value used in plotting, None for default value.
    vmax : float
        Luminance maximum value used in plotting, None for default value.
    cmap : str or None
        Matplotlib colormap name. None will use the default colormap for
        the field being plotted as specified by the Py-ART configuration.
    title : str
        Title to label plot with, None to use default title generated from
        the field and sweep parameters. Parameter is ignored if title_flag
        is False.
    title_flag : bool
        Set to True to add a title to the plot, False does not add a title.
    axislabels : (str, str)
        2-tuple of x-axis, y-axis labels. None for either label will use
        the default axis label. Parameter is ignored if axislabels_flag is
        False.
    axislabels_flag : bool
        True to add label the axes, False does not label the axes.
    colorbar_flag : bool
        True to add a colorbar with label to the axis. False leaves off
        the colorbar.
    colorbar_label : str
        Colorbar label, None will use a default label generated from the
        field information.
    colorbar_orient : 'vertical' or 'horizontal'
        Colorbar orientation.
    noplot : boolean
        Switch to indicate if a plot should be created or just return the values.

    Returns
    -------
    dict : dictionary
        A dictionary with values for
        max = Maximum data value
        min = Maximum data value
        az_max = Azimuth value for maximum data value, hopefully in center of corner reflector
        el_max = Elevation value for maximum data value, hopefully in center of corner reflector
        el_top = Elevation value for top of corner reflector
        range = Distance to target
    """

    if fig is None and ax is None and noplot is False:
        fig, ax = plt.subplots()

    return_dic = {'max': None, 'min': None, 'az_max': None,
                  'el_max': None, 'el_top': None, 'range': None, 'fig': None}

    # Get data and coordinate information
    az = obj[az_field].values
    el = obj[el_field].values
    rng = obj[range_field].values
    data = obj[field].values

    if az_limits is not None or el_limits is not None:
        if az_limits is not None:
            az_limits.sort()
            az_index = (az >= az_limits[0]) & (az <= az_limits[1])
        else:
            az_index = np.full(az.size, True)

        if el_limits is not None:
            el_limits.sort()
            el_index = (el >= el_limits[0]) & (el <= el_limits[1])
        else:
            el_index = np.full(el.size, True)

        index = az_index & el_index
        if np.sum(index) < 1:
            print('Unable to extract data within azimuth or elevation limts. '
                  'Returning without calculating value or making plot.')
            return return_dic

        az = az[index]
        el = el[index]
        data = data[index, :]

    if target_limits is not None:
        target_limits.sort()
        index = (rng >= target_limits[0]) & (rng <= target_limits[1])

        if np.sum(index) < 1:
            print('Unable to extract data within range limts. '
                  'Returning without calculating value or making plot.')
            return return_dic

        rng = rng[index]
        data = data[:, index]

    min_az = np.nanmin(az)
    max_az = np.nanmax(az)
    min_el = np.nanmin(el)
    max_el = np.nanmax(el)

    if delta_x is None:
        delta_x = max_az - min_az
    if delta_y is None:
        delta_y = max_el - min_el

    # Get range closest to target_range
    if target_range is None:
        index = np.nanargmax(data)
        index = np.unravel_index(index, data.shape)
        target_range = rng[index[1]]

    target_index = np.argmin(np.abs(np.array(rng) - target_range))
    target_range = rng[target_index]

    data = data[:, target_index]

    # Get azimuth and elevation onto a meshgrid
    xi, yi = np.meshgrid(np.linspace(min_az, max_az, int(delta_x / 0.01)),
                         np.linspace(min_el, max_el, int(delta_y / 0.01)))

    # Grid up the data for plotting
    grid = griddata((az, el), data, (xi, yi), method='linear')
    max_ind = np.unravel_index(np.nanargmax(grid), grid.shape)
    try:
        diff = copy.deepcopy(grid[slice(max_ind[0] + 1, grid.shape[1]), max_ind[1]])
        diff[diff < -20] = np.nan
        top_index = np.nanargmin(np.diff(diff))
    except ValueError:
        try:
            diff = grid[slice(max_ind[0] + 1, grid.shape[1]), max_ind[1]]
            diff = np.array(diff)
            top_index = np.nanargmin(np.diff(diff))
        except ValueError:
            print('Unable to correctly grid data. Returning without calculating value or making plot.')
            return return_dic

    top_index += max_ind[0]
    top_index = (top_index, max_ind[1])

    data_max = grid[max_ind]
    data_min = np.nanmin(grid)
    az_max = xi[max_ind]
    el_max = yi[max_ind]
    el_top = yi[top_index]

    maxstr = 'Max: ' + str(round(data_max, 2))
    minstr = 'Min: ' + str(round(data_min, 2))
    azstr = 'Az (max): ' + str(round(az_max, 1))
    elstr = 'El (max): ' + str(round(el_max, 1))
    eltopstr = 'El (top): ' + str(round(el_top, 1))
    rngstr = 'Range: ' + str(round(target_range, 1))

    # Plot data using pcolormesh
    return_fig = None
    if noplot is False:
        pm = ax.pcolormesh(xi[0, :], yi[:, 0], grid, vmin=vmin, vmax=vmax, cmap=cmap, shading='auto')
        ax.plot(xi[max_ind], yi[max_ind], 'w+', ms=10)
        ax.plot(xi[max_ind], yi[top_index], 'wx', ms=10)

        # Add text information
        ax.text(0.88, 0.9, maxstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.87, minstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.84, azstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.81, elstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.78, eltopstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.75, rngstr, fontsize=8, transform=plt.gcf().transFigure)

        if title_flag is True:
            if title is None:
                time_str = pd.to_datetime(str(obj['time'].values[0]))
                title = ' '.join(['Corner Reflector', field.title(),
                                  time_str.strftime('%Y-%m-%d %H:%M:%S')])
            ax.set_title(title)

        if axislabels_flag is True:
            try:
                az_units = obj[az_field].attrs['units']
                el_units = obj[el_field].attrs['units']
            except KeyError:
                az_units = 'degree'
                el_units = 'degree'

            if axislabels[0] is None:
                axislabels[0] = f"Azimuth ({az_units})"

            if axislabels[1] is None:
                axislabels[1] = f"Elevation ({el_units})"

            ax.set_xlabel(axislabels[0])
            ax.set_ylabel(axislabels[1])

        if colorbar_flag:
            if colorbar_label is None:
                colorbar_label = field.title() + ' (' + obj[field].attrs['units'] + ')'

            fig.colorbar(mappable=pm, label=colorbar_label,
                         orientation=colorbar_orient, ax=ax)

            return_fig = fig

    return_dic['max'] = data_max
    return_dic['min'] = data_min
    return_dic['az_max'] = az_max
    return_dic['el_max'] = el_max
    return_dic['el_top'] = el_top
    return_dic['range'] = target_range
    return_dic['fig'] = return_fig

    return return_dic
