# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 17:43:34 2020

@author: qo18712
"""


"""
-5.3 Openstreetmap query
"""
import json
from osmxtract import overpass
import geopandas as gpd
import subprocess
from itertools import chain
import re

def osm_query(bounds,tag_bl,tag_h,inepsg,outepsg,output_jsonfile,output_shpfile,output_shpfile_clean):
    """
    

    Parameters
    ----------
    bounds : tuple
        (xmin,ymin,xmax,ymax) define the boundary of the query.
    tag_bl : string
        key word to match the osm building information,it is 'building:levels' as building levels query.
    tag_h : string
        key word to match the osm building information,it is 'height' as building height query.
    inepsg : string
        reference system of json_file in the format 'epsg:epsg_num'.
        it is 'epsg:4326' for openstreetmap data
    outepsg : string
        reference system of the desired output shapefilem, in the format 'epsg:epsg_num'.
        it is 'epsg:32633' for Berlin example.
    output_jsonfile : jsonfile name
        full filename of output jsonfile.
    output_shpfile : shapefile name
        full filename of the output shapefile.
    output_shpfile_clean : cleaned shapefile name
        full filename of the output shapefile with building geomtry 
        with (area_val > 500000) or (area_val <=0.1) excluded.

    Returns
    -------
    geodataframe1 : geopandas geodataframe
        the geodataframe of output_shpfile_clean.

    """
    #building level query
    query_bl = overpass.ql_query(bounds, tag=tag_bl,timeout=100)
    response = overpass.request(query_bl)
    feature_collection = overpass.as_geojson(response, 'polygon')
        
    #building height query
    query_bh = overpass.ql_query(bounds, tag=tag_h,timeout=100)
    response_bh = overpass.request(query_bh)
    feature_collection_bh = overpass.as_geojson(response_bh, 'polygon')
    
    outjson = dict(type='FeatureCollection', features=[])
    #merge the two query results, building level and building height
    outjson['features']=feature_collection['features'] + feature_collection_bh['features']
    
    #outjson_copy = outjson.copy()
    
    # Write as GeoJSON
    featurelist = list()
    keywords = [tag_bl,tag_h]
    num = 0
    for i in range(len(outjson['features'])):
        feature = outjson['features'][i]
        #ensure at least three coordinates in the geometry
        coor = feature.geometry.coordinates
        point_num = len(list(chain(*coor)))
        if point_num >=3:
            keywords_match = set(keywords) &set(feature.properties.keys())            
            for x in keywords:
                if x in feature.properties:
                    #get numbers from string
                    val = re.findall(r'\d+',feature.properties[x])
                    if len(val)==2:
                        #convert height to number
                        feature.properties[x] = int(val[0])+float(int(val[1])/10)                    
                    elif len(val)==0:
                        feature.properties[x] = 0
                    else:
                        feature.properties[x] = float(val[0])
            #only save interesting keywords  
            interested_att = {x: feature.properties[x] for x in keywords if x in feature.properties}
            feature.properties = interested_att
            #both height and levels exist
            if len(keywords_match)>1:
                if (feature.properties[tag_h]!=0):                    
                        featurelist.append(feature)
            #only height or only levels exist 
            elif len(keywords_match)==1:
                keywords_match = list(keywords_match)[0]
                if (feature.properties[keywords_match]!=0):
                    featurelist.append(feature)
        else:
            num += 1
            print('Bad values were spotted!')
            print(feature)
    #bad values
                
    outjson_final = dict(type='FeatureCollection', features=[])
    outjson_final['features'] = featurelist 
    with open(output_jsonfile, 'w') as f:
         json.dump(outjson_final,f)    
     #convert geojson to shapefile
    args = ['ogr2ogr', '-f', 'ESRI Shapefile',\
            output_shpfile, output_jsonfile,
            '-s_srs', inepsg, '-t_srs',outepsg ]
    subprocess.Popen(args)
    #calculate areas to exclude bad values
    geodataframe = gpd.GeoDataFrame.from_file(output_shpfile)
    geodataframe['area'] = geodataframe.geometry.area
    num_list = list()
    for i in range(len(geodataframe)):
        area_val= geodataframe.loc[i]['area']
        #exclude areas>500000 or areas<0.1 features
        if (area_val > 500000) or (area_val <=0.1):
            num_list.append(i)
    
    geodataframe1=geodataframe.drop(num_list)
    geodataframe1.to_file(output_shpfile_clean)
    return geodataframe1
