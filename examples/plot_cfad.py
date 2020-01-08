import radtraq
import glob
import act
import matplotlib.pyplot as plt
import numpy as np

f = radtraq.tests.sample_files.EXAMPLE_KAZR
obj = act.io.armfiles.read_netcdf(f)

# CFAD Test
hist, x, y = radtraq.plotting.cfad.calc_cfad(obj,'reflectivity_copol', 'range')
display = radtraq.plotting.cfad.plot_cfad(hist, x, y)
plt.show()
