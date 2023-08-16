"""
Example on how to calculate and plot cloud masks
------------------------------------------------

This example shows how to calculate a cloud mask and plot data

"""


import radtraq
import act
import matplotlib.pyplot as plt

# Read in sample data using ACT
ds = act.io.armfiles.read_netcdf(radtraq.tests.sample_files.EXAMPLE_KAZR)

# Resample data for ease of processing
ds = ds.resample(time='1min').nearest()

# Calculate and apply cloud mask
ds = radtraq.proc.cloud_mask.calc_cloud_mask(ds, 'reflectivity_copol')
ds = ds.where(ds['cloud_mask_2'] == 1)

# Plot data using ACT
display = act.plotting.TimeSeriesDisplay(ds)
display.plot('reflectivity_copol', cmap='jet')
display.axes[0].set_ylim([0, 20000])
plt.show()

ds.close()
