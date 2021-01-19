# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:51:06 2020

@author: qo18712
"""
from osgeo import gdal
from osgeo import ogr
from osgeo import gdalconst
def shp2raster(tifile,shpfile,attribute,outputfile):
    """
    convert shapefile to raster by refering the grid and coordination system of a reference geotiff.

    Parameters
    ----------
    tifile : geotiff
        the filename of reference geotiff whose grid, resolution 
        and coordination system will be applied to the outputfile.
    shpfile : shapefile
        the input name of the shapefile.
    attribute : string
        the field of the shapefile data that will be used to convert to geotiff.
    outputfile : geotiff
        the output filename.

    Returns
    -------
    None.

    """
    

    data = gdal.Open(tifile, gdalconst.GA_ReadOnly)
    geo_transform = data.GetGeoTransform()
    proj = data.GetProjection()
    source_layer = data.GetLayer()
    x_min = geo_transform[0]
    y_max = geo_transform[3]
    x_max = x_min + geo_transform[1] * data.RasterXSize
    y_min = y_max + geo_transform[5] * data.RasterYSize
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    mb_v = ogr.Open(shpfile)
    mb_l = mb_v.GetLayer()
    field_names = [field.name for field in mb_l.schema]
    print(field_names)
    pixel_width = geo_transform[1]
    target_ds = gdal.GetDriverByName('GTiff').Create(outputfile, x_res, y_res, 1, gdal.GDT_Float32)
    target_ds.SetGeoTransform(data.GetGeoTransform())
    
    band = target_ds.GetRasterBand(1)
    NoData_value = -99999
    band.SetNoDataValue(NoData_value)
    band.FlushCache()
    #gdal.RasterizeLayer(target_ds, [1], mb_l, options=gdal.RasterizeOptions(attribute="ITEM2012",outputSRS=proj))
    
    
    #keyword for options need to be the name of the field
    #but here, also Forests was designated, "green urban areas" in the fields was also converted to raster
    #gdal.RasterizeLayer(target_ds, [1], mb_l, options=["ITEM2012=Forests"])
    gdal.RasterizeLayer(target_ds, [1], mb_l, options = ["ALL_TOUCHED=TRUE",attribute],burn_values=[1])
    target_ds.SetProjection(proj)
    target_ds = None