"""
Example on how to calculate and plot cfad
-----------------------------------------

This example shows how to calculate and plot a cfad

"""

import matplotlib.pyplot as plt
from act.io.armfiles import read_netcdf

import radtraq

# Read in example data
ds = read_netcdf(radtraq.tests.sample_files.EXAMPLE_KAZR)

# Calculate CFAD histogram
data_array = radtraq.plotting.cfad.calc_cfad(ds, 'reflectivity_copol')

# Plot CFAD histogram
dims = data_array.dims
display = radtraq.plotting.cfad.plot_cfad(data_array, data_array[dims[1]], data_array[dims[0]])
plt.show()
