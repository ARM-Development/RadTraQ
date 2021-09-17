"""
Example on how to plot out a corner reflector raster
----------------------------------------------------

This example shows how to plot out a corner reflector
raster scan which also analyzes the data and returns
the corner reflector location information

"""


from radtraq.tests.sample_files import EXAMPLE_RASTER
from radtraq.plotting.corner_reflector import plot_cr_raster
from act.io.armfiles import read_netcdf
import matplotlib.pyplot as plt

# Read in sample data using ACT
obj = read_netcdf(EXAMPLE_RASTER)

# Process and plot raster file
data = plot_cr_raster(obj, target_range=478., el_limits=[-0.5, 2.5], noplot=False)
plt.show()
obj.close()
