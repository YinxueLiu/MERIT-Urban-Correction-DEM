# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 21:13:14 2020

@author: qo18712
-2020,April,29
read raster
"""
import numpy as np
from osgeo import gdal
def DEM_Read(src):
    """
    

    Parameters
    ----------
    src : geotiff
        full filename of the tif to be read.

    Returns
    -------
    Qcal : numpy array in 2d
        the values of the geotiff in 2d numpy array.
    nodata : float
        nodata value of the input geotiff.

    """
    #read raster as array
    ds = gdal.Open(src, gdal.GA_ReadOnly)
    band = ds.GetRasterBand(1)
    Qcal = np.array(band.ReadAsArray())
     #get none value
    nodata = band.GetNoDataValue()
    #reshape the 2D array to 1D
    #Qcal_scatter = Qcal.reshape(Qcal.shape[0]*Qcal.shape[1],1)
    #Ele = Qcal[Qcal != nodata]
    # create a new array store the raster value from tiff
    # and add a new column as pixel number index  
    return Qcal,nodata

