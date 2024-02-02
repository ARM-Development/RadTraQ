"""
Example on how to plot out a corner reflector raster
----------------------------------------------------

This example shows how to plot out a corner reflector
raster scan which also analyzes the data and returns
the corner reflector location information

"""

import matplotlib.pyplot as plt
from act.io.arm import read_arm_netcdf
from open_radar_data import DATASETS

import radtraq

# Read in sample data using ACT
filename = DATASETS.fetch('sgpkasacrcrrasterC1.a1.20130419.012153.nc')
ds = read_arm_netcdf(filename)

# Process and plot raster file
data = radtraq.plotting.corner_reflector.plot_cr_raster(
    ds, target_range=478.0, el_limits=[-0.5, 2.5], noplot=False
)
plt.show()
ds.close()
