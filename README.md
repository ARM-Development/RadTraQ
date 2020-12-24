# RadTraQ
Radar Tracking of Quality

![](https://github.com/ARM-Development/RadTraQ/workflows/RadTRAQ/badge.svg)

Work in progress!

This is a repository of codes that were initially coded up in IDL in the ARM DQ Office for use with the ARM cloud radars.  In transitioning the code to python, it makes sense to open-source it so that others can benefit and even provide back.  Currently, the code is using dask to quickly calculate and plot up CFADs and calculate the noise floor based on code from Pavlos Kollias and Ieng Jo while they were with McGill University.

Kollias, P., I. Jo, P. Borque, A. Tatarevic, K. Lamer, N. Bharadwaj, K. Widener, K. Johnson, and E.E. Clothiaux, 2014: Scanning ARM Cloud Radars. Part II: Data Quality Control and Processing. J. Atmos. Oceanic Technol., 31, 583–598, https://doi.org/10.1175/JTECH-D-13-00045.1

Code to come includes using the noise floor to calculate the cloud mask, retrieve vertical average profiles of radar variables in cloud, and more.
