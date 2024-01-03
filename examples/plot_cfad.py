"""
Example on how to calculate and plot cfad
-----------------------------------------

This example shows how to calculate and plot a cfad

"""

import radtraq
from act.io.arm import read_arm_netcdf
import matplotlib.pyplot as plt

# Read in example data
ds = read_arm_netcdf(radtraq.tests.sample_files.EXAMPLE_KAZR)

# Calculate CFAD histogram
data_array = radtraq.plotting.cfad.calc_cfad(ds, 'reflectivity_copol')

# Plot CFAD histogram
dims = data_array.dims
display = radtraq.plotting.cfad.plot_cfad(data_array, data_array[dims[1]], data_array[dims[0]])
plt.show()
