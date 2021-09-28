"""
============
radtraq.proc
============

.. currentmodule:: radtraq.proc

This module contains procedures for creating a cloud mask.

.. autosummary::
    :toctree: generated/

    calc_avg_profile
    calc_cloud_mask
    calc_noise_floor
    extract_profile
    extract_profile_at_lat_lon

"""

from .cloud_mask import calc_cloud_mask
from .noise import calc_noise_floor
from .profile import calc_avg_profile
from .profile import extract_profile
from .profile import extract_profile_at_lat_lon
