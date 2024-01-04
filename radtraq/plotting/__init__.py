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
    plot_self_consistency

"""

from .cfad import calc_cfad  # noqa
from .cfad import plot_cfad  # noqa
from .profile import plot_avg_profile  # noqa
from .corner_reflector import plot_cr_raster  # noqa
from .self_consistency import plot_self_consistency  # noqa
