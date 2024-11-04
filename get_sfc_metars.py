#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# User inputs
debug = 1
test = True
secsPerDay = 86400
pastSecs = secsPerDay/6   # 4 hours
deltaBetweenFiles = secsPerDay / 24
#lastForecastHour = 6
metarUrl = 'http://weather.rap.ucar.edu/surface'
targetDirBase = '/home/disk/bob/s2noclime/sfc/metars'
tempDir = '/tmp'
products = ['metars_den','metars_cod','metars_abq']
catalogPrefix = 'surface.GTS_Station_Plot'

# Field Catalog inputs
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/s2noclime'
else:
    ftpCatalogServer = 'catalog-ingest.eol.ucar.edu'
    ftpCatalogUser = 's2noclime'
    ftpCatalogPwd = 'St0rmPeak!'
    catalogDestDir = '/pub/incoming/catalog/s2noclime'

# Open ftp connection to NCAR sever
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
catalogFTP.cwd(catalogDestDir)

# get current date and hour
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowHourStr = now.strftime("%H")
nowDateHourStr = nowDateStr+nowHourStr
if debug:
    print("nowDateHourStr = ", nowDateHourStr)

# compute start time
pastDelta = timedelta(0, pastSecs)
nowDateHour = datetime.strptime(nowDateHourStr,'%Y%m%d%H')
startTime = nowDateHour - pastDelta
startDateHourStr = startTime.strftime("%Y%m%d%H")
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print("startDateHourStr = ", startDateHourStr)

# set up list of date-hour combos to be checked
nFiles = int(pastSecs / deltaBetweenFiles)
dateHourStrList = []
for iFile in range(0, nFiles):
    deltaSecs = timedelta(0, iFile * deltaBetweenFiles)
    dayTime = now - deltaSecs
    dateStr = dayTime.strftime("%Y%m%d")
    dateHourStr = dayTime.strftime("%Y%m%d%H")
    dateHourStrList.append(dateHourStr)
if debug:
    print("dateHourStrList = ", dateHourStrList)

# get list of files meeting criteria from url
urlFileList = []
for t in range(0,nFiles):
    currentFileTime = dateHourStrList[t]
    for i in range(0,len(products)):
        # get list of files on server for this time and this product
        nextFile = currentFileTime+'_'+products[i]+'.gif'
        urlFileList.append(nextFile)
if debug:
    print("urlFileList = ", urlFileList)

# if files in urlFileList not in localFileList, download, rename & ftp them
if len(urlFileList) == 0:
    if debug:
        print("WARNING: no data on server")
else:
    # make sure targetBaseDir directory exists and cd to it
    if not os.path.exists(targetDirBase):
        os.makedirs(targetDirBase)
    os.chdir(targetDirBase)
    
    # get local file list - i.e. those which have already been downloaded
    localFileList = os.listdir('.')
    if debug:
        print("  localFileList: ", localFileList)

    # loop through the url file list, downloading those that have
    # not yet been downloaded
    for idx,urlFileName in enumerate(urlFileList,0):
        if debug:
            print("  idx = ", idx," and urlFileName = ",urlFileName)

        if urlFileName not in localFileList:
            if debug:
                print("   ",urlFileName,"not in localFileList -- get file")
            try:
                command = 'wget '+metarUrl+'/'+urlFileName
                os.system(command)
            except Exception as e:
                print("    wget failed, exception: ", e)
                continue

            # rename file and move to wftpserver
            # first get forecast_hour
            (base,ext) = os.path.splitext(urlFileName)
            (dateTime,junk,location) = base.split('_')
            if location == 'abq':
                region = 'AlbequerqueNM_Region'
            elif location == 'cod':
                region = 'CodyWY_Region'
            elif location = 'den':
                region = 'DenverCO_Region'
            else:
                print('No region called '+location)
            catalogName = catalogPrefix+'.'+dateTime+'00.'+region+'.gif'
            if debug:
                print("   catalogName = ", catalogName)

            # copy file to tmpDir as catalogName
            shutil.copy(targetDirBase+'/'+urlFileName,
                        tempDir+'/'+catalogName)

            # ftp file to catalog
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()
            if debug:
                print('   ftpd',catalogName,'to NCAR FC\n')

            # remove file from tempDir
            os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()






    

                              
