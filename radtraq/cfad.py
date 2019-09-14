import numpy as np
import matplotlib.pyplot as plt


def plot_cfad(hist, x, y):

    fig, ax = plt.subplots()
    cs = ax.contourf(x, y, hist, 50)
    cbar = fig.colorbar(cs)
    plt.show()
    

def calc_cfad(obj, variable, hvariable, xbins=None, log=True, yint=20):
    #Currently assuming vertical point data from netcdf files
    data = obj[variable]
    height = obj[hvariable]

    if xbins is None:
        xbins = np.linspace(-70, 50, 121)
    print(xbins)

    hist = []
    for j, ht in enumerate(height):
        h, bin_edge =  np.histogram(data[:,j:j+yint], bins=xbins)
        if log is True:
            h = np.log10(h)
        hist.append(list(h))
        j += yint

    return hist, xbins[:-1], height
