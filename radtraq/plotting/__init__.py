"""
================
radtraq.plotting
================

.. currentmodule:: radtraq.plotting

This module contains procedures for plotting
various aspects of the data

.. autosummary::
    :toctree: generated/

    calc_cfad
    plot_cfad
    plot_avg_profile
    plot_cr_raster

"""

from .cfad import calc_cfad
from .cfad import plot_cfad
from .profile import plot_avg_profile
from .corner_reflector import plot_cr_raster
