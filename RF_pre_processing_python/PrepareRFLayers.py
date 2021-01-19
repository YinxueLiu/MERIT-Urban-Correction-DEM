# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 16:47:10 2020

@author: yinxue.liu@bristol.ac.uk

-2020/11/13
pre-processing of random forest layers-take data for Berlin, Germany for example
To apply this to another location, you will need to change the parameters in the function-
downloadMERIT, the city boundary file- bounfile, the offset between the target city's
vertical reference system and EGM96, and the input and output SRS.
This script include the process of generating 
MERIT,
NTL,
POP,
LIDAR,
Slope,
Neighbour+ELE(in csv),
Building Height，
Building Density layers.
The process of get MERIT applies for Night-Time-Lights,Population density, just replace the 'tifilename' and 
/the corresponding projected filename
"""

"""
-1
prepare MERIT data/Night-Times-Lights/Population density

1) download MERIT data 
please find the details of username and password for download at
 http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_DEM/
2) clip data by city boundary and define the projection system (UTM30N in this case)
"""
import os
from osgeo import gdal
import downloadMERIT

#1)
pathre =  r'C:\Users\qo18712\OneDrive - University of Bristol\Meeting\202005\\' #download location
tif_zone = 'dem_tif_n30e000.tar'
tilename = 'n50e010_dem.tif'
username = '*'
password = '*' 
tifilename = downloadMERIT.MERIT_download(tif_zone,tilename,username,password,pathre)

#2)
import clip_proj    
city = 'Berlin'
pathre = r'D:\Berlin_example\\'
bounfile = r'D:\RF_server\Berlin_1\Diff\Berlin_SRTM_m_diff_RasterDomain.shp' 
filename = tifilename #downloaded MERIT file name
filename_proj = pathre+city+'_MERIT_'+'proj.tif'
inSRS = 'EPSG:4326' #WGS84
outSRS = 'EPSG:32633' #UTM_30N
merit_final,bound_val = clip_proj.clip_proj(city,pathre,bounfile,inSRS,outSRS,filename,filename_proj)

"""
-2 Night-Time-Lights

1)download Night-Time-Lights at https://www.ngdc.noaa.gov/eog/viirs/download_dnb_composites.html, 
in this case year of 2015 was used in the research.
2)clip and resample the downloaded Night-Time-Lights to match the grid of MERIT
"""
import resample
#1)
downloaded_NTL = 'NTL.tif' #replace with the fullpath with the downloaded NTL file
#2)
NTL_final = 'NTL_final.tif' 
resampleM = gdal.GRA_Bilinear
resample.matchgrid(downloaded_NTL,merit_final,NTL_final,resampleM)

"""
-3 Population density

1)download population density at https://www.worldpop.org/geodata/listing?id=29, 
in this case year of 2015 was used in the research.
2)clip and resample the downloaded Night-Time-Lights to match the grid of MERIT
"""
#1)
downloaded_POP = 'POP.tif' #replace with the fullpath with the downloaded POP file
#2)
POP_final = 'POP_final.tif' 
resampleM = gdal.GRA_Bilinear
resample.matchgrid(downloaded_POP,merit_final,POP_final,resampleM)

"""
-4
prepare lidar data.
1) download the lidar data
it usually are ascii tiles, need to merge them.
2) resample LIDAR data to the same resolution of your MERIT DEM
3) convert LIDAR layer to the EGM96 which is the vertical reference system of MERIT DEM
EGM96 = DHHN92-0.711m
"""

import readraster
import arraytoRaster

#1)
offset = 0.711
lidarfile = r'D:\Berlin_example\Berlin_Lidar.tif'

#2)
#resample lidar dtm by average
src_filename = lidarfile
match_filename = merit_final
dst_filename = pathre+os.path.splitext(os.path.basename(lidarfile))[0]+\
    '_resampled'+os.path.splitext(os.path.basename(lidarfile))[1]
resampleM = gdal.GRA_Average
resample.matchgrid(src_filename,match_filename,dst_filename,resampleM)

#3)
#convert to the EGM96 vertical system
lidarfile_final = pathre+os.path.splitext(os.path.basename(dst_filename))[0]+\
    '_EGM96'+os.path.splitext(os.path.basename(dst_filename))[1]
arr,nodata = readraster.DEM_Read(dst_filename)
arr[arr!=nodata] = arr[arr!=nodata] - offset
arraytoRaster.array_to_raster(arr, dst_filename, lidarfile_final)

"""
-5 
slope file
Slope layer is calculated from MERIT DEM

"""
import Cal_Slope
demfile = merit_final #the output MERIT DEM from step 1
layername = 'slope'
slopefile = pathre+city+'_MERIT_'+layername+'.tif'
Cal_Slope.calculate_slope(demfile,slopefile)

"""
-6
Neighbour_values and elevation
"""
import GetNeighbourvalues as gnv
layername = '_NeighELE'
outputcsv = pathre+city+layername+'.csv'
gnv.Neighbourascsv(demfile,outputcsv)

"""
-7 & -8
building density file & building height file
building footprint data(shapefile) can be downloaded from http://download.geofabrik.de/europe/germany.html
building height data can be downloaded from https://overpass-turbo.eu/
*note the downloaded building height is in GeoJson format
below codes(step 1)- step 5)) show the process of downloading building information from Openstreetmap of target city,
and process the downloaded file to buildingdensity and buildingheight layer with the same grid of MERIT DEM.

"""

"""
1) create fishnet of merit dem
"""
import Fishnet
rasterfile = merit_final
fishnet_filename = pathre+'Berlin_merit_fishnet4.shp'
epsg_num = '32633'
xres,yres=Fishnet.fishnet(rasterfile, fishnet_filename, epsg_num)

from pyproj import Proj,transform

"""
2) get the boundary of interested areas
"""
#get the polygon_areas within MERIT grid
#as the openStreetMap query takes lon,lat as bounds
#convert bounding_box from projected system to lat and lon
inProj = Proj("epsg:32633") #projection code of reference tiff file
outProj = Proj("epsg:4326") #wgs84
xmin,ymin = transform(inProj,outProj,bound_val[0],bound_val[1])
xmax,ymax = transform(inProj,outProj,bound_val[2],bound_val[3])
bounds = (xmin,ymin,xmax,ymax)

"""
3) Openstreetmap query
"""
import OsmQuery
bounds = bounds
tag_bl = 'building:levels'
tag_h ='height'
inepsg = 'EPSG:4326'   
outepsg =  'EPSG:32633'
output_jsonfile = 'Berlin_building_level_height.geojson'  
output_shpfile = 'Berlin_building_level_height1.shp'  
output_shpfile_clean = 'Berlin_building_level_height1_clean1.shp'  
geodataframe = OsmQuery.osm_query(bounds,tag_bl,tag_h,inepsg,outepsg,output_jsonfile,output_shpfile,output_shpfile_clean)

"""
4)
get the intersection areas between fishnet and buildingheight shapefile,
attributes of the intersected grid
zonal statistics of areas of intersected, and averaged building height
passed the zonal statistics back to fishnet
"""
import OsmBuildingConvert as obc
field_overlapareas = 'areaOver'
tag_bl = 'building:levels'
tag_h = 'height'
geodataframe = geodataframe
output_overlayfile = 'Berlin_building_level_height1_clean1_fishnet4_overlay.shp'
layername_bd = 'BD'
layername_bh = 'height'
output_bdfile = pathre+city+'_'+layername_bd+'.shp'
output_bhfile = pathre+city+'_'+layername_bh+'.shp'
obc.osm_building(geodataframe,fishnet_filename,field_overlapareas,tag_bl,tag_h,xres,yres, \
                 pathre,city,output_overlayfile,output_bdfile,output_bhfile)
"""

5) end
convert fishnet to raster
"""    
#convert shapefile to raster by certain attribute
import ShptoRaster
shpfile = output_bdfile
attribute = "ATTRIBUTE="+layername_bd
layername = '_'+layername_bd
outputfile = pathre+city+layername+'.tif'
ShptoRaster.shp2raster(merit_final,shpfile,attribute,outputfile)

shpfile = output_bhfile
attribute = "ATTRIBUTE="+layername_bh
layername = '_'+layername_bh
outputfile = pathre+city+layername+'.tif'
ShptoRaster.shp2raster(merit_final,shpfile,attribute,outputfile)


