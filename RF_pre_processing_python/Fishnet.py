# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 16:55:15 2020

@author: qo18712
This script generates projected fishnet in shapefile format
the fishnet grids are the grid of the input rasterfile.
"""
from osgeo import ogr,osr,gdal
import numpy as np
import os
gdal.UseExceptions()
def getWKT_PRJ (epsg_code):
    """
    

    Parameters
    ----------
    epsg_code : string
        the epsg number of the coordination system.

    Returns
    -------
    output : string
        the coordination system of the input epsg number.

    """ 
    import urllib
    # access projection information
    wkt = urllib.request.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code))
    # remove spaces between charachters
    #here are something with bytes, this b
    remove_spaces = wkt.read().replace(b" ",b"")
    # place all the text on one line
    output = remove_spaces.replace(b"\n", b"")
    return output
 
def fishnet(rasterfile,fishnet_filename,epsg_num):
    """
    

    Parameters
    ----------
    rasterfile : geotiff
        full filename of the tif file which will be used to create the grid.
    fishnet_filename : shapefile
        the filename of the output fishnet file.
    epsg_num : int
        the epsg_num of the desired system of the fishnet shapefile.

    Returns
    -------
    xres : float
        grid length of created fishnet.
    yres : float
        grid height of created fishnet.

    """
    ds_refer = gdal.Open(rasterfile)
    geotrans = ds_refer.GetGeoTransform()
    output_shp = fishnet_filename
    prj_wkt = ds_refer.GetProjection()
    drv = ogr.GetDriverByName('ESRI Shapefile')
    
    if os.path.exists(output_shp):
        # DeleteDataSource will delete related files, compared to os.remove
        drv.DeleteDataSource(output_shp)
    
    # grid definition
    # extent
    # resolution of MERIT
    xres = geotrans[1]
    yres = geotrans[5]
    xsize = ds_refer.RasterXSize
    ysize = ds_refer.RasterYSize
    ulx, uly, lrx, lry = geotrans[0],geotrans[3],geotrans[0]+xsize*xres,geotrans[3]+ysize*yres
    
    # half the resolution
    dx = xres/2
    dy = yres/2
    # center coordinates
    xx, yy = np.meshgrid(
        np.arange(ulx+dx, lrx+dx, xres), 
        np.arange(uly+dy, lry+dy, yres),
    )
    #Initialize the output shapefile:
    ds = drv.CreateDataSource(output_shp)
    lyr = ds.CreateLayer(output_shp, geom_type=ogr.wkbPolygon)
    fdefn = lyr.GetLayerDefn()
    
    #Loop over each center coordinate and add the polygon to the output:
    for x,y in zip(xx.ravel(), yy.ravel()):
        poly_wkt = f'POLYGON (({x-dx} {y-dy}, {x+dx} {y-dy}, {x+dx} {y+dy}, {x-dx} {y+dy}, {x-dx} {y-dy}))'
    
        ft = ogr.Feature(fdefn)
        ft.SetGeometry(ogr.CreateGeometryFromWkt(poly_wkt))
        lyr.CreateFeature(ft)
        ft = None
    #create projection file manually
    prj = open(os.path.dirname(output_shp)+'\\'+ \
               os.path.splitext(os.path.basename(output_shp))[0]+'.prj', 'w')
    epsg = getWKT_PRJ(epsg_num)
    #convert byte to str by decode
    prj.write(epsg.decode('utf-8'))
    prj.close()
    lyr = None
    ds = None
    return xres,yres

