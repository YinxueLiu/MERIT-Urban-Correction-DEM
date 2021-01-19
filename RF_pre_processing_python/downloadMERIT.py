# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 15:22:51 2020

@author: qo18712
-2020/12/08
fetch data from certain website which requires username and password

"""
#download MERIT data
import requests
import tarfile

def MERIT_download(tif_zone,tilename,username,password,pathre):
    '''
    

    Parameters
    ----------
    tif_zone : filename of the .tar file (MERIT in geotiff format used)
        the MERIT DEM was segamented from by each 30longitude(S60-N90), 30latitude(E000-W180).
    tilename : tif file name inside the specified tile
        when unzip the downloaded .tar file, there are multiple tif image by different lat, lon.
    username : authention username 
    password : authention password
    please find way to get username and password at this page http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_DEM/
    or please contact to the developer (yamadai [at] iis.u-tokyo.ac.jp) to get an access.
    pathre : path to save downloaded .tar file and extracted tif tile

    Returns
    -------
    full filename of extracted MERIT DEM file.

    '''    

    username = '*' 
    password = '*' 
    url = 'http://'+username+':'+password+ \
    '@hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_DEM/distribute/v1.0.2/'+\
        tif_zone
    r = requests.get(url,stream=True)
    downloadfile =pathre+tif_zone
    with open(downloadfile, \
              'wb') as f:
        f.write(r.content)
        
    #extract file from tar
    tar = tarfile.open(downloadfile)
    for member in tar.getmembers():
        name = tif_zone.split('.')[0]+'/'+tilename
        if name in member.name:
            tar.extract(member,path=pathre) 
    #get the fullfile name of extracted MERIT DEM
    merit_demfile = pathre+name
    return merit_demfile



