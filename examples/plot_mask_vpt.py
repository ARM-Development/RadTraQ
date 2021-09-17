"""
Example on how to calculate and plot average profiles
-----------------------------------------------------

This example shows how to calculate and plot average profiles
from masked data

"""


from radtraq.tests.sample_files import EXAMPLE_KAZR
from radtraq.proc.cloud_mask import calc_cloud_mask
from radtraq.proc.profile import calc_avg_profile
from radtraq.plotting import plot_avg_profile
from act.io.armfiles import read_netcdf
import matplotlib.pyplot as plt
import numpy as np

# Read in Example KAZR File using ACT
obj = read_netcdf(EXAMPLE_KAZR)

# Resample to 1-minute to simplify processing
obj = obj.resample(time='1min').nearest()

# Process cloud mask in order to properly produce average VPT profiles through cloud
obj = calc_cloud_mask(obj, 'reflectivity_copol')

# Variables to calculate average profiles
variable = ['reflectivity_copol', 'mean_doppler_velocity_copol', 'reflectivity_xpol']

# Create a grid to interpolate data onto - Needed for different radars
first_height = 1500.
ygrid = np.arange(first_height, 15000, 50)

# Calculate average profiles
obj = calc_avg_profile(obj, variable=variable, first_height=first_height, ygrid=ygrid)

# Showing how to do this for multiple radars
# Set up dictionary for profile comparison plotting
rad_dict = {'sgpkazrgeC1.b1': {'object': obj, 'variable': variable[0]},
            'sgpkazrge2C1.b1': {'object': obj, 'variable': variable[0]},
            'sgpkazrmdC1.b1': {'object': obj, 'variable': 'reflectivity_xpol'},
            'sgpkazrmd2C1.b1': {'object': obj, 'variable': 'reflectivity_xpol'}
            }

# Plot up profiles and perform comparisons from data in dictionary
display = plot_avg_profile(rad_dict)

# Show plot
plt.show()

# Close out object
obj.close()
