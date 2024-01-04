"""
=============
radtraq.utils
=============

.. currentmodule:: radtraq.utils

This module contains various utilities

.. autosummary::
    :toctree: generated/

    calculate_azimuth_distance_from_lat_lon
    calculate_dual_dop_lobes
    calc_ground_range_and_height
    get_height_variable_name
    range_correction
"""

from .corrections import range_correction  # noqa
from .dataset_utils import get_height_variable_name  # noqa
from .utils import calculate_azimuth_distance_from_lat_lon  # noqa
from .utils import calculate_dual_dop_lobes  # noqa
from .utils import calc_ground_range_and_height  # noqa
