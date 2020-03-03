"""
Example on how to calculate and plot cfad
-----------------------------------------

This example shows how to calculate and plot a cfad

"""


import radtraq
import act
import matplotlib.pyplot as plt

# Read in example data
f = radtraq.tests.sample_files.EXAMPLE_KAZR
print(f)
obj = act.io.armfiles.read_netcdf(f)

# Calculate CFAD histogram
hist, x, y = radtraq.plotting.cfad.calc_cfad(obj, 'reflectivity_copol', 'range')

# Plot CFAD histogram
display = radtraq.plotting.cfad.plot_cfad(hist, x, y)
plt.show()
