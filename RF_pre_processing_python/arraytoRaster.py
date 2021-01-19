# -*- coding: utf-8 -*-
"""
Created on Thu May  7 09:35:11 2020

@author: qo18712
"""
import numpy as np
from osgeo import gdal,gdalconst
gdal.UseExceptions()

def array_to_raster(array,referfilename,dst_filename,*args,**kwargs):
    """
    

    Parameters
    ----------
    array : numpy array-2d
        the array to be saved as geotiff.
    referfilename : string
        full filename of the tif file that provides the reference info.
    dst_filename : string
        output filename of the saved geotiff with the array as values.
    *args : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    refer_ds = gdal.Open(referfilename, gdalconst.GA_ReadOnly)

    refer_proj = refer_ds.GetProjection()
    refer_geotrans = refer_ds.GetGeoTransform()
    wide = refer_ds.RasterXSize
    high = refer_ds.RasterYSize
    wkt_projection = refer_proj

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(dst_filename, wide, high, 1, gdalconst.GDT_Float32)

    dataset.SetGeoTransform(refer_geotrans)  
    ndv = kwargs.get("ndv", -99999)
    dataset.GetRasterBand(1).SetNoDataValue(ndv)#set nodata value
    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
    refer_ds = None
    dataset = None
    #return dataset, dataset.GetRasterBand(1)  #If you need to return, remenber to return  also the dataset because the band don`t live without dataset.
    
#save array as int
def array_to_rasterInt(array,referfilename,dst_filename,*args,**kwargs):
    """
    

    Parameters
    ----------
    array : numpy array-2d
        the array to be saved as geotiff.
    referfilename : string
        full filename of the tif file that provides the reference info.
    dst_filename : string
        output filename of the saved geotiff with the array as values.
    *args : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    array=array.astype(np.int32)
    refer_ds = gdal.Open(referfilename, gdalconst.GA_ReadOnly)

    refer_proj = refer_ds.GetProjection()
    refer_geotrans = refer_ds.GetGeoTransform()
    wide = refer_ds.RasterXSize
    high = refer_ds.RasterYSize
    wkt_projection = refer_proj

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(dst_filename, wide, high, 1, gdalconst.GDT_Int32)

    dataset.SetGeoTransform(refer_geotrans)  
    ndv = kwargs.get("ndv", -99999)
    dataset.GetRasterBand(1).SetNoDataValue(ndv)#set nodata value
    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
    refer_ds = None
    dataset = None