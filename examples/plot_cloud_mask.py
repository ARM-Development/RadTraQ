"""
Example on how to calculate and plot cloud masks
------------------------------------------------

This example shows how to calculate a cloud mask and plot data

"""


import radtraq
import act
import matplotlib.pyplot as plt

# Read in sample data using ACT
f = radtraq.tests.sample_files.EXAMPLE_KAZR
obj = act.io.armfiles.read_netcdf(f)

# Resample data for ease of processing
ge = obj.resample(time='1min').nearest()

# Calculate and apply cloud mask
ge = radtraq.proc.cloud_mask.calc_cloud_mask(ge, 'reflectivity_copol', 'range')
ge = ge.where(ge['mask2'] == 1)

# Plot data using ACT
display = act.plotting.TimeSeriesDisplay(ge)
display.plot('reflectivity_copol', cmap='jet')
display.axes[0].set_ylim([0, 20000])
plt.show()

ge.close()
