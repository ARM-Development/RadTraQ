"""
Example on how to calculate and plot cfad
-----------------------------------------

This example shows how to calculate and plot a cfad

"""

import matplotlib.pyplot as plt
from act.io.arm import read_arm_netcdf
from open_radar_data import DATASETS

import radtraq

# Read in example data
filename = DATASETS.fetch('sgpkazrgeC1.a1.20190529.000002.cdf')
ds = read_arm_netcdf(filename)

# Calculate CFAD histogram
data_array = radtraq.plotting.cfad.calc_cfad(ds, 'reflectivity_copol')

# Plot CFAD histogram
dims = data_array.dims
display = radtraq.plotting.cfad.plot_cfad(data_array, data_array[dims[1]], data_array[dims[0]])
plt.show()
