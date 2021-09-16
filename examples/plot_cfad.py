"""
Example on how to calculate and plot cfad
-----------------------------------------

This example shows how to calculate and plot a cfad

"""


from radtraq.plotting.cfad import calc_cfad, plot_cfad
from radtraq.tests.sample_files import EXAMPLE_KAZR
from act.io.armfiles import read_netcdf
import matplotlib.pyplot as plt

# Read in example data
obj = read_netcdf(EXAMPLE_KAZR)

# Calculate CFAD histogram
data_array = calc_cfad(obj, 'reflectivity_copol')
dims = data_array.dims

# Plot CFAD histogram
display = plot_cfad(data_array, data_array[dims[1]], data_array[dims[0]])
plt.show()
