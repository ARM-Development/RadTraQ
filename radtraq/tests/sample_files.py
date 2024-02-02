"""
act.tests.sample_files
======================

Sample data file for use in testing. These files should only
be used for testing ACT.

-- autosummary::
    :toctree: generated/

    EXAMPLE_KAZR
    EXAMPLE_RASTER
    EXAMPLE_PPI
    EXAMPLE_RHI
    EXAMPLE_XSAPR
    EXAMPLE_CSAPR

"""
from open_radar_data import DATASETS

EXAMPLE_KAZR = DATASETS.fetch('sgpkazrgeC1.a1.20190529.000002.cdf')
EXAMPLE_RASTER = DATASETS.fetch('sgpkasacrcrrasterC1.a1.20130419.012153.nc')
EXAMPLE_PPI = DATASETS.fetch('houkasacrcfrM1.a1.20210922.150006.nc')
EXAMPLE_RHI = DATASETS.fetch('houkasacrcfrM1.a1.20211122.164124.nc')
EXAMPLE_XSAPR = DATASETS.fetch('sgpxsaprcfrvptI4.a1.20200205.100827.nc')
EXAMPLE_CSAPR = DATASETS.fetch('csapr.nc')
