# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 16:53:43 2020

@author: qo18712
"""

from osgeo import gdal, gdalconst
gdal.UseExceptions()
def matchgrid(src_filename,match_filename,dst_filename,resampleM):
    """
    

    Parameters
    ----------
    src_filename : geotiff
        filename of the file to be processed.
    match_filename : geotiff
        filename that provides the reference grid and projection system.
    dst_filename : geotiff
        filename of the output file.
    resampleM : gdal.GRA_
        resample method when resampling.

    Returns
    -------
    None.

    """
    # Source
    src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
    src_proj = src.GetProjection()
    #src_geotrans = src.GetGeoTransform()

    # We want a section of source that matches this:
    match_ds = gdal.Open(match_filename, gdalconst.GA_ReadOnly)
    #got problem here
    #works by setting PROJ_LIB to the location of proj.db in environment setting manually
    match_proj = match_ds.GetProjection()#this code returns empty
    '''
    #create a projection manually
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3067)
    '''
    match_geotrans = match_ds.GetGeoTransform()

    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize

    # Output / destination
    
    driver = gdal.GetDriverByName('GTiff')
    dst = driver.Create(dst_filename, wide, high, 1, gdalconst.GDT_Float32)
    dst.SetGeoTransform( match_geotrans )
    dst.SetProjection(match_proj)
    #dst = driver.CreateCopy(dst_filename,match_ds)
    #ndv = -99999
    #ndv = -9999
    #dst.GetRasterBand(1).SetNoDataValue(ndv)#set nodata value
    # Do the work
    #gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_Bilinear)
    gdal.Warp(dst,src,options=gdal.WarpOptions(srcSRS=src_proj,dstSRS=match_proj,srcNodata=-9999,dstNodata=-9999,resampleAlg=resampleM))
    del dst # Flush
