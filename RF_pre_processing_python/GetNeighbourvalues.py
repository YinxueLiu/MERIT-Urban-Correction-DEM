# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 09:34:46 2019

@author: qo18712
-2020/11/15
define as a function
"""
#still some problems with edge data 
#get neighbours values
import numpy as np
from osgeo import gdal
import pandas as pd 

def Neighbourascsv(demfile,outputcsv):
    """
    

    Parameters
    ----------
    demfile : geotiff
        full filename of the demfile.
    outputcsv : csv
        the elevation values and their 8 neighbour elevation values,
        each row represents one pixel of the input demfile.

    Returns
    -------
    None.

    """
    ds = gdal.Open(demfile, gdal.GA_ReadOnly)
    Qcal = np.array(ds.GetRasterBand(1).ReadAsArray())
        
    #use size of original raster array to get neighbours value
    row = np.shape(Qcal)[0]
    col = np.shape(Qcal)[1]
    
    # use a list to store neighbours value
    m = 0
    Neighb = []
    Xoffset = (-1, 0, 1)
    Yoffset = (-1, 0, 1)
    for i in range(0, row):
    
             for j in range(0, col):
                         for a in Xoffset:
                             for b in Yoffset:
    
                               if (i + a) in range(0, row) and 0<= (j + b) < col:
                                  
                                  Neighb.append(Qcal[i + a][j + b])
                                  #print (i + a, j + b)
                     
                               else:
                                    #print (i+a, j+b)
                                    m += 1
                                    for m in range(0,m): 
                                      Neighb.append(None)
                     
             m = 0                 
    newRow = row * col                 
    Neighb1 = np.reshape(Neighb,(newRow,9))# reshape data 
    pd.DataFrame(Neighb1).to_csv(outputcsv)
'''
path = 'D:\\RF_server\\Berlin\\city\\NO forest\\'
src = 'Berlin_MERIT_m_masked.tif'
demfile = path + src
outputcsv = 'D:\\RF_server\\Berlin\\RF_final\\NO forest\\Berlin city_NeighbFile.csv'
Neighbourascsv(demfile,outputcsv)
'''