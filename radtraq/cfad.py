import numpy as np
import matplotlib.pyplot as plt


def plot_cfad(hist, x, y):

    fig, ax = plt.subplots()
    cs = ax.contourf(x, y, hist, 50)
    plt.show()
    

def calc_cfad(obj, variable, hvariable, xbins=None, log=True):
    #Currently assuming vertical point data from netcdf files
    data = obj[variable]
    height = obj[hvariable]

    if xbins is None:
        xbins = np.linspace(-70, 40, 111)

    hist = []
    for j, ht in enumerate(height):
        h, bin_edge =  np.histogram(data[:,j], bins=xbins)
        if log is True:
            h = np.log10(h)
        hist.append(list(h))

    return hist, xbins[:-1], height
