# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 12:02:05 2020

@author: qo18712
"""
from osgeo import gdal
import geopandas as gpd

def clip_proj(city,pathre,bounfile,inSRS,outSRS,filename,filename_proj):
    """    
    Parameters
    ----------
    city : string
        name of the target city.
    pathre : path
        path to save the output file.
    bounfile : shapefile
        the full path of the boundary file of the target city.
    inSRS : string
        the coordination system of the file to be projected.
    outSRS : string
        name of the projection system that the input file is about to be defined.
    filename : filename, tif
        name of file to be cliped and projected.
    filename_proj : filename, tif
        full filename of the clip and projected file.

    Returns
    -------
    filename_proj : filename
        the filename of the clip and projected file.
    bound_val : boundary in tuple
        the (xmin,ymin,xmax,ymax) of the target city domain
    """

    #clip raster by shapefile
    #bounfile is the city boundary
    #bounfile is supposed to be file with projection
    boun = gpd.read_file(bounfile)
    bound_val = boun.geometry.total_bounds
    
    
    #clip MERIT with city boundary file
    #define projection system by gdalwarp
    #'EPSG:32633' = UTM 33N, projection system of LIDAR
    #  outputBounds --- output bounds as (minX, minY, maxX, maxY) in target SRS
    #  outputBoundsSRS --- SRS in which output bounds are expressed, in the case they are not expressed in dstSRS
    warpoption = gdal.WarpOptions(srcSRS=inSRS,dstSRS=outSRS,outputBounds=bound_val,\
                                  outputBoundsSRS=outSRS)
    gdal.Warp(filename_proj,filename,options=warpoption)
    #os.remove(tifilename) #remove the unprojected tif file
    return filename_proj,bound_val