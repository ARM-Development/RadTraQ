===========================================
Radar Tracking of Quality Toolkit (RadTraQ)
===========================================

|Build| |Docs| |DOI|

.. |Docs| image:: https://github.com/ARM-Development/RadTraQ/actions/workflows/documentation.yml/badge.svg
    :target: https://github.com/ARM-Development/RadTraQ/actions/workflows/documentation.yml

.. |Build| image:: https://github.com/ARM-Development/RadTraQ/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/ARM-Development/RadTraQ/actions/workflows/ci.yml

.. |DOI| image:: https://zenodo.org/badge/281182712.svg
    :target: https://zenodo.org/doi/10.5281/zenodo.8253245

RadTraQ is a python library housing routines related to assessing and monitoring
the quality of a radar's quality and calibration. This library is a work in progress,
currently housing scipts to plot radar CFADs, plot and analyze corner reflector
scans, calculate noise floors, create cloud masks, and plot up average profiles
for comparisons.

Check out the `documentation <https://arm-development.github.io/RadTraQ/build/html/index.html>`_
and `example gallery <https://arm-development.github.io/RadTraQ/build/html/source/auto_examples/index.html>`_ for more details.

Papers that these routines are based on will be listed in the documentation for
each relevant function.

|Reflector| |CloudMask| |VPT|

.. |Reflector| image:: https://arm-development.github.io/RadTraQ/build/html/_images/sphx_glr_plot_corner_reflector_raster_001.png
               :target: https://arm-development.github.io/RadTraQ/build/html/_images/sphx_glr_plot_corner_reflector_raster_001.png
               :height: 150
.. |CloudMask| image:: https://arm-development.github.io/RadTraQ/build/html/_images/sphx_glr_plot_cloud_mask_001.png
               :target: https://arm-development.github.io/RadTraQ/build/html/_images/sphx_glr_plot_cloud_mask_001.png
               :height: 150
.. |VPT| image:: https://arm-development.github.io/RadTraQ/build/html/_images/sphx_glr_plot_mask_vpt_001.png
         :target: https://arm-development.github.io/RadTraQ/build/html/_images/sphx_glr_plot_mask_vpt_001.png
         :height: 150

Installation
~~~~~~~~~~~~

RadTraQ is installable using pip::

    pip install radtraq

and Conda::

    conda install -c conda-forge radtraq

Contributing
~~~~~~~~~~~~

We welcome contributions for all uses of RadTraQ, provided the code can be
distributed under the BSD 3-clause license. A copy of this license is
available in the **LICENSE** file in this directory.
