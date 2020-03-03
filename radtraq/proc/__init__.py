"""
============
radtraq.proc
============

.. currentmodule:: radtraq.proc

This module contains procedures for creating a cloud mask.

.. autosummary::
    :toctree: generated/

    calc_cloud_mask
    calc_noise_floor
    calc_avg_profile

"""

from .cloud_mask import calc_cloud_mask
from .noise import calc_noise_floor
from .profile import calc_avg_profile
