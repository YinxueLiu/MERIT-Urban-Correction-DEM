# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 16:03:53 2020

@author: qo18712
"""
from osgeo import gdal
import rasterio

def calculate_slope(DEMfile,slopefile):
    """
    

    Parameters
    ----------
    DEMfile : geotiff
        full filename of the dem where the slope will be calculated.
    slopefile : geotiff
        full filename of the output slope file.

    Returns
    -------
    slope : numpy array in 2d
        the slope values in 2d numpy array.

    """
    gdal.DEMProcessing(slopefile, DEMfile, 'slope')
    with rasterio.open(slopefile) as dataset:
        slope=dataset.read(1)
    return slope