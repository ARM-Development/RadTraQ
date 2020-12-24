import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import pandas as pd



def plot_cr_raster(obj, field='reflectivity', target_range=None, ax=None, fig=None,
                   delta_x=None, delta_y=None, az_limits=None, el_limits=None,
                   vmin=None, vmax=None, cmap=None, title=None, title_flag=True,
                   axislabels=[None, None], axislabels_flag=True,
                   colorbar_flag=True, colorbar_label=None,
                   colorbar_orient='vertical', noplot=True):
    """
    Plot a corner reflector raster scan

    Parameters
    ----------
    field : String
        Field to plot if other than reflectivity
    target_range : Float
        Estimated range of the corner reflector

    Other Parameters
    ----------------
    ax : Axis
        Axis to plot on. None will use the current axis.
    fig : Figure
        Figure to add the colorbar to. None will use the current figure.
    delta_x : Float
        Azimuth grid spacing for griddata
    delta_y : Float
        Elevation grid spacing for griddata
    az_limits : list
        Azimuth limits in form [min, max]
    el_limits : list
        Elevation limits in form [min, max]
    vmin : float
        Luminance minimum value, None for default value.
    vmax : float
        Luminance maximum value, None for default value.
    cmap : str or None
        Matplotlib colormap name. None will use the default colormap for
        the field being plotted as specified by the Py-ART configuration.
    title : str
        Title to label plot with, None to use default title generated from
        the field and sweep parameters. Parameter is ignored if title_flag
        is False.
    title_flag : bool
        True to add a title to the plot, False does not add a title.
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
    ticks : array
        Colorbar custom tick label locations.
    ticklabs : array
        Colorbar custom tick labels.
    colorbar_orient : 'vertical' or 'horizontal'
        Colorbar orientation.

    """

    if fig is None and ax is None and noplot is False:
        fig, ax = plt.subplots()

    # Get data and coordinate information
    az = obj['azimuth'].values
    el = obj['elevation'].values
    rng = obj['range'].values
    data = obj[field].values

    # Calculate delta for x and y
    if az_limits is None:
        min_az = np.nanmin(az)
        max_az = np.nanmax(az)
    else:
        min_az = az_limits[0]
        max_az = az_limits[1]

    if el_limits is None:
        min_el = np.nanmin(el)
        max_el = np.nanmax(el)
    else:
        min_el = el_limits[0]
        max_el = el_limits[1]

    if delta_x is None:
        delta_x = max_az-min_az
    if delta_y is None:
        delta_y = max_el-min_el

    # Get range closest to target_range
    if target_range is None:
        target_index = 0
    else:
        target_index = np.argmin(np.abs(np.array(rng) - target_range))

    data = data[:, target_index]

    # Get azimuth and elevation onto a meshgrid
    xi, yi = np.meshgrid(np.linspace(min_az, max_az, int(delta_x/0.01)),
                         np.linspace(min_el, max_el, int(delta_y/0.01)))

    # Grid up the data for plotting
    grid = griddata((az, el), data, (xi, yi), method='linear')
    max_ind = np.unravel_index(np.nanargmax(grid), grid.shape)
    diff = np.diff(grid[:, max_ind[0]], n=1)
    idx = (diff == np.nanmin(diff))
    diff_index = np.where(idx)[0][-1]
    maxstr = 'Max: ' + str(round(grid[max_ind],2))
    minstr = 'Min: ' + str(round(np.nanmin(grid),2))
    azstr = 'Az (max): ' + str(round(xi[max_ind],1))
    elstr = 'El (max): ' + str(round(yi[max_ind],1))
    eltopstr = 'El (top): ' + str(round(yi[diff_index, max_ind[1]],1))

    # Plot data using pcolormesh
    if noplot is False:
        pm = ax.pcolormesh(xi[0, :], yi[:, 0], grid, vmin=vmin, vmax=vmax, cmap=cmap)
        ax.plot(xi[max_ind], yi[max_ind], 'w+', ms=10)
        ax.plot(xi[max_ind], yi[diff_index,max_ind[1]], 'wx', ms=10)

        # Add text information
        ax.text(0.88, 0.9, maxstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.87, minstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.84, azstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.81, elstr, fontsize=8, transform=plt.gcf().transFigure)
        ax.text(0.88, 0.78, eltopstr, fontsize=8, transform=plt.gcf().transFigure)

        if title_flag is True:
            if title is None:
                time_str = pd.to_datetime(str(obj['time'].values[0]))
                title = ' '.join(['Corner Reflector', field.title(), time_str.strftime('%m/%d/%Y %H:%M:%S')])
            ax.set_title(title)

        if axislabels_flag is True:
            if axislabels[0] is None:
                axislabels[0] = 'Azimuth (deg)'
            if axislabels[1] is None:
                axislabels[1] = 'Elevation (deg)'
            ax.set_xlabel(axislabels[0])
            ax.set_ylabel(axislabels[1])

        if colorbar_flag:
            if colorbar_label is None:
                colorbar_label = field.title() + ' (' + obj[field].attrs['units'] + ')'
            fig.colorbar(mappable=pm, label=colorbar_label, orientation=colorbar_orient,
                         ax=ax)

    return {'max': grid[max_ind], 'min': np.nanmin(grid), 'az_max': xi[max_ind],
            'el_max': yi[max_ind], 'el_top': yi[diff_index, max_ind[1]]}
