"""
Example on how to plot out a corner reflector raster
----------------------------------------------------

This example shows how to plot out a corner reflector
raster scan which also analyzes the data and returns
the corner reflector location information

"""


import matplotlib.pyplot as plt
from act.io.armfiles import read_netcdf

import radtraq

# Read in sample data using ACT
ds = read_netcdf(radtraq.tests.sample_files.EXAMPLE_RASTER)

# Process and plot raster file
data = radtraq.plotting.corner_reflector.plot_cr_raster(
    ds, target_range=478.0, el_limits=[-0.5, 2.5], noplot=False
)
plt.show()
ds.close()
