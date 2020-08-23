"""
Example on how to plot out a corner reflector raster
----------------------------------------------------

This example shows how to plot out a corner reflector
raster scan which also analyzes the data and returns
the corner reflector location information

"""


import radtraq
import act
import matplotlib.pyplot as plt

# Read in sample data using ACT
f = radtraq.tests.sample_files.EXAMPLE_RASTER
obj = act.io.armfiles.read_netcdf(f)

# Process and plot raster file
data = radtraq.plotting.corner_reflector.plot_cr_raster(obj, target_range=478.,
                                                      el_limits=[-0.5, 2.5], noplot=False)
print(data)

plt.show()
obj.close()
