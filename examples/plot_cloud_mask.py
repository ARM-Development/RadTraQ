"""
Example on how to calculate and plot cloud masks
------------------------------------------------

This example shows how to calculate a cloud mask and plot data

"""


from radtraq.tests.sample_files import EXAMPLE_KAZR
from radtraq.proc.cloud_mask import calc_cloud_mask
import act
import matplotlib.pyplot as plt

# Read in sample data using ACT
obj = act.io.armfiles.read_netcdf(EXAMPLE_KAZR)

# Resample data for ease of processing
obj = obj.resample(time='1min').nearest()

# Calculate and apply cloud mask
obj = calc_cloud_mask(obj, 'reflectivity_copol')
obj = obj.where(obj['cloud_mask_2'] == 1)

# Plot data using ACT
display = act.plotting.TimeSeriesDisplay(obj)
display.plot('reflectivity_copol', cmap='jet')
display.axes[0].set_ylim([0, 20000])
plt.show()

obj.close()
