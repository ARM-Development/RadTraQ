"""
act.tests.sample_files
======================

Sample data file for use in testing. These files should only
be used for testing ACT.

-- autosummary::
    :toctree: generated/

    EXAMPLE_KAZR
"""
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

EXAMPLE_KAZR = os.path.join(DATA_PATH, 'sgpkazrgeC1.a1.20190529.000002.cdf')
EXAMPLE_RASTER = os.path.join(DATA_PATH, 'sgpkasacrcrrasterC1.a1.20130419.012153.nc')
