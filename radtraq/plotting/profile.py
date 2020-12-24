"""
radtraq.plotting.profile
------------------------

Module for plotting up average variable
profiles based on masked data

"""

import matplotlib.pyplot as plt
import numpy as np


def plot_avg_profile(rad_dict, ylim=[0, None]):
    """
    Function for plotting up average profiles including differences

    Parameters
    ----------
    rad_dict : dict
        Dictionary of objects and variables to process.  See example
    ylim : list
        ylimits to use

    Returns
    -------
    ax : matplotlib ax handle
        Returns the axis handle for additional updates if needed

    """

    # Set up figure
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    # Process each sub-dictionary in the dictionary passed in
    all_plat = []
    all_mean = []
    for d in rad_dict:
        all_plat.append(d)
        variable = rad_dict[d]['variable']
        obj = rad_dict[d]['object']

        # Get dimensions and use data from non-time dimension for y-axis
        dims = list(obj[variable].dims)
        height = [d for d in dims if 'time' not in d][0]

        # Plot average profiles
        ax[0].plot(obj[variable+'_avg_prof'], obj[height], label=d)

        # Add mean profiles to one array
        all_mean.append(obj[variable+'_avg_prof'].values)
        height_units = obj[height].attrs['units']

    # Set up plot and add legend
    ax[0].set_ylim(ylim)
    ax[0].set_ylabel(height + ' (' + height_units + ')')
    ax[0].legend(fontsize=8)

    # Process and plot differences between each radar/object passed in
    diff_name = []
    for i, p in enumerate(all_plat):
        for j, p2 in enumerate(all_plat):
            # If same object then continue
            if p == p2:
                continue

            # Track the comparisons and continue if already done
            diff_name.append([p, p2])
            u, ind, ct = np.unique(diff_name, return_inverse=True, return_counts=True)
            if 1 not in ct:
                continue

            # Calculate differences, make label, and plot
            diff = all_mean[j] - all_mean[i]
            lab = ' '.join([p2, '-', p+':', str(round(np.nanmean(diff), 2))])
            ax[1].plot(diff, rad_dict[p]['object'][height], label=lab)

    # Set up plot and add legend
    ax[1].set_ylim(ylim)
    ax[1].legend(fontsize=8)

    plt.tight_layout()

    return ax
