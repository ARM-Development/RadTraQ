"""
Example on how to calculate and plot cloud masks
------------------------------------------------

This example shows how to calculate a cloud mask and plot data

"""


import radtraq
import act
import matplotlib.pyplot as plt

# Read in sample data using ACT
obj = act.io.armfiles.read_netcdf(radtraq.tests.sample_files.EXAMPLE_KAZR)

# Resample data for ease of processing
obj = obj.resample(time='1min').nearest()

# Calculate and apply cloud mask
obj = radtraq.proc.cloud_mask.calc_cloud_mask(obj, 'reflectivity_copol')
obj = obj.where(obj['cloud_mask_2'] == 1)

# Plot data using ACT
display = act.plotting.TimeSeriesDisplay(obj)
display.plot('reflectivity_copol', cmap='jet')
display.axes[0].set_ylim([0, 20000])
plt.show()

obj.close()
