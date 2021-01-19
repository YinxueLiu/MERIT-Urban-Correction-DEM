# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 17:46:39 2020

@author: qo18712
"""


"""
-5.4
get the intersection areas between fishnet and buildingheight shapefile,
attributes of the intersected grid
zonal statistics of areas of intersected, and averaged building height
passed the zonal statistics back to fishnet
"""
import geopandas as gpd
import numpy as np

def osm_building(geodataframe,fishnet_filename,field_overlapareas,tag_bl,tag_h,xres,yres, \
                 pathre,city,output_overlayfile,output_bdfile,output_bhfile):
    """
    join fields from geodataframe to the created fishnet (grids of merit dem)

    Parameters
    ----------
    geodataframe : geopandas geodataframe
        the geodataframe created from osmquery.
    fishnet_filename : string
        full filename of the created fishnet.
    field_overlapareas : TYPE
        DESCRIPTION.
    tag_bl : string
        the key word to locate the field of the acquired geodataframe, should be 'building:levels' in osm building.
    tag_h : string
        the key word to locate the field of the acquired geodataframe, should be 'height' in osm building.
    xres : float
        length of the input fishnet grid.
    yres : float
        width of the input fishnet grid.
    pathre : path
        path of output location.
    city : string
        name of the target city.
    output_overlayfile : filename of shapefile
        full filename of the overlayed shapefile between fishnet and geodataframe from osm query.
    output_bdfile : filename of shapefile
        full filename of the shapefile which has the building density as one of the field.
    output_bhfile : filename of shapefile
        full filename of the shapefile which has the building height as one of the field.

    Returns
    -------
    None.

    """
    fishnet_geodf = gpd.GeoDataFrame.from_file(fishnet_filename)
    fishnet_geodf = fishnet_geodf.reset_index(drop=True)
    geodataframe_final = geodataframe.reset_index(drop=True)
    geodf_overlay = gpd.overlay(geodataframe_final,fishnet_geodf,how='intersection')
    #calculate areaO of overlaied shapefile
    geodf_overlay[field_overlapareas] = geodf_overlay.geometry.area
    geodf_overlay.to_file(output_overlayfile)
    
    
    #building density
    sum_area_df = geodf_overlay.groupby('FID', as_index=False).agg({field_overlapareas: 'sum'})
    #value to fishnet_geodf
    merged_fishnet_geodf = fishnet_geodf.merge(sum_area_df, how = 'left', on = ['FID'])
    merged_fishnet_geodf['BD'] = merged_fishnet_geodf[field_overlapareas]/(xres*(-yres))
    merged_fishnet_geodf['BD'] = np.where(merged_fishnet_geodf['BD'] > 1, \
                                       1,merged_fishnet_geodf['BD'])
    merged_fishnet_geodf.to_file(output_bdfile)
    
    
    #building height
    floor_h = 3 #assume each floor is 3m
    #subset = building height = 0 replace with building_level*floor_height
    geodf_overlay[tag_h] = np.where(geodf_overlay[tag_h] == 0, \
                                       geodf_overlay[tag_bl]*floor_h,geodf_overlay[tag_h])
    ave_height_df = geodf_overlay.groupby('FID', as_index=False).agg({tag_h: 'mean'})
    #value to fishnet_geodf
    merged_fishnet_geodf_bh = fishnet_geodf.merge(ave_height_df, how = 'left', on = ['FID'])
    merged_fishnet_geodf_bh.to_file(output_bhfile)