#!/usr/bin/python3

# Runs are at 00 and 12Z

import os
import shutil
import time
import datetime
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil
from ftplib import FTP

def listFD(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

# full URL: https://weather.rap.ucar.edu/data/upper/YYYYMMDD/YYMMDD_hhmmss_upaCNTR_850.gif
url = 'https://weather.rap.ucar.edu/data/upper'
type = 'upaCNTR'
products = {'850':'850_mb_chart',
            '700':'700_mb_chart',
            '500':'500_mb_chart',
            '250':'250_mb_chart'}

localDirBase = '/home/disk/bob/s2noclime/upperair/ucar'
tempDir = '/tmp'
catalogPrefix = 'upperair.Constant_Pressure'
catalogSuffix = '_mb_chart'
ext = 'gif'
debug = True
test = True

# Field Catalog inputs
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/s2noclime'
else:
    ftpCatalogServer = 'catalog-ingest.eol.ucar.edu'
    ftpCatalogUser = 's2noclime'
    ftpCatalogPassword = 'St0rmPeak!'
    catalogDestDir = '/pub/incoming/catalog/s2noclime'

# Open ftp connection to NCAR sever
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

# Get current date and time
now = datetime.utcnow()
nowDateStr = now.strftime("%Y%m%d")
nowDateTimeStr = now.strftime("%Y%m%d%H%M%S")
startTime = now - timedelta(1)
startDateStr = startTime.strftime("%Y%m%d")
startDateTimeStr = startTime.strftime("%Y%m%d%H%M%S")
if debug:
    print('nowDateTimeStr = ',nowDateTimeStr)
    
# List of dates to check for new data
dateStrList = [startDateStr,nowDateStr]

# Get list of files of interest on UCAR server from last 24 hours
for date in dateStrList:
    ucarFileList = []
    ucarFileDate = []
    ucarFileTime = []
    ucarFileLevel = []
    for file in listFD(url+'/'+date, ext):
        tmp = os.path.basename(file)
        (base,ext) = os.path.splitext(tmp)
        (fdate,ftime,ftype,level) = base.split('_')
        if ftype == type and level in products.keys() and fdate >= startDateStr:
            ucarFileList.append(tmp)
            ucarFileDate.append(fdate)
            ucarFileTime.append(ftime)
            ucarFileLevel.append(level)

    # Go to localDir and download files that are not present
    localDir = os.path.join(localDirBase,date)
    if not os.path.exists(localDir):
        os.makedirs(localDir)
    os.chdir(localDir)
    localFileList = os.listdir('.')
    for idx,ucarFileName in enumerate(ucarFileList,0):
        if ucarFileName not in localFileList:

            command = 'wget '+url+'/'+ucarFileDate[idx]+'/'+ucarFileName
            os.system(command)

            catalogName = catalogPrefix+'.'+ucarFileDate[idx]+ucarFileTime[idx]+'.'+ucarFileLevel[idx]+catalogSuffix+ext
            shutil.copy(ucarFileName,
                        tempDir+'/'+catalogName)
            
            # ftp file to catalog location
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()

            # remove file from tempDir
            os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
