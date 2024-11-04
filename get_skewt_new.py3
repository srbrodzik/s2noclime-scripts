#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
import shutil
from ftplib import FTP
import paramiko

# user inputs
debug = True
test = False
binDir = '/home/disk/bob/s2noclime/bin'

if test:
    sftpCatalogHostName = 'ftp.atmos.washington.edu'
    port = 22
    sftpCatalogUserName = 'anonymous'
    sftpCatalogPassword = 'brodzik@uw.edu'
    sftpCatalogDestDir = 'brodzik/incoming/s2noclime'
else:
    sftpCatalogHostName = 'catalog-ingest.eol.ucar.edu'
    port = 22
    sftpCatalogUserName = 's2noclime'
    sftpCatalogPassword = 'St0rmPeak!'
    sftpCatalogDestDir = 's2noclime'

out_base_dir = '/home/disk/bob/s2noclime/upperair/nws'
max_ht = 7
secsPerDay = 86400
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 0
startDate = '20230131'
# set number of days to go back from startDate
num_days = 1

hourList = ['00','03','06','09','12','15','18','21']
siteList = {'72681':{'long_name':'Boise_ID','short_name':'OIS'},
            '72476':{'long_name':'GrandJunction_CO','short_name':'GJT'},
            '72672':{'long_name':'Riverton_WY','short_name':'RIW'},
	    '72572':{'long_name':'SaltLakeCity_UT','short_name':'SLC'}
}
numHours = len(hourList)
numSites = len(siteList)
outfile_prefix = 'upperair.SkewT'
outfile_wb_suffix = '_Wet_Bulb'

# Get start date
if startFlag == 0:
    nowTime = time.gmtime()
    now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                   nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
else:
    nowDateStr = startDate
    now = datetime.strptime(nowDateStr,'%Y%m%d')

nowDateStr = now.strftime("%Y%m%d")
nowYearStr = now.strftime("%Y")
nowMonthStr = now.strftime("%m")
nowDayStr = now.strftime("%d")

# Make list of dates to process
dateStrList = []
yearStrList = []
monthStrList = []
dayStrList = []
for idate in range(0,num_days):
    deltaSecs = timedelta(0, idate * secsPerDay)
    nextDate = now - deltaSecs
    nextDateStr = nextDate.strftime("%Y%m%d")
    dateStrList.append(nextDateStr)
    nextYearStr = nextDate.strftime("%Y")
    yearStrList.append(nextYearStr)
    nextMonthStr = nextDate.strftime("%m")
    monthStrList.append(nextMonthStr)
    nextDayStr = nextDate.strftime("%d")
    dayStrList.append(nextDayStr)
print('dateStrList = ',dateStrList)
   
# Go to data directory
os.chdir(out_base_dir)

for idx,idate in enumerate(dateStrList,0):

    # define year, month and day
    year = yearStrList[idx]
    month = monthStrList[idx]
    day = dayStrList[idx]

    # define date dirs and create them if necessary
    out_dir = out_base_dir+'/'+idate
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # get list of files in out_dir
    out_dir_files = os.listdir(out_dir)
            
    # cd to out_dir
    os.chdir(out_dir)
            
    for site in siteList:

        print('site = ', siteList[site])

        for hour in hourList:

            print('hour =', hour)

            # define output file names
            outFile_skewt = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['long_name']+'.png'
            outFile_wetbulb = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['long_name']+outfile_wb_suffix+'.png'
            outFile_html = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['short_name']+'.html'
            (base,ext) = os.path.splitext(outFile_html)

            # Check to make sure we don't already have data for this hour
            if not outFile_html in out_dir_files:

                # get ascii data
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',}
                urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+site

                # make sure url exists
                get = requests.get(urlStr, headers=headers)
                if get.status_code == 200:
                    command = "lwp-request '"+urlStr+"' > "+outFile_html
                    os.system(command)
                    #print('Done getting html file')

                    # check filesize of html file
                    fileSize = os.path.getsize(outFile_html)
                    if fileSize <= 3000:
                        #print('html file too small - go to next hour')
                        os.remove(outFile_html)
                    else:
                        print('html file okay - create skewt & wetbulb files')
                
                        # Remove html tags from file
                        command = binDir+'/removeHtmlTags.csh '+outFile_html+' '+base+'.txt'
                        os.system(command)
                
                        # Remove missing data records from file
                        command = binDir+'/removeLinesWithMissingData.py '+base+'.txt '+base+'.new'
                        os.system(command)

                        #print('Done creating txt and new files from html file')
                        
                        # Create ssh client
                        ssh_client = paramiko.SSHClient()
                        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                        # Connect to sftp server
                        ssh_client.connect(sftpCatalogHostName,port,sftpCatalogUserName,sftpCatalogPassword)
                        
                        # Create the sftp client
                        sftp = ssh_client.open_sftp()

                        # Create skewt and move to field catalog directory
                        localSkewtPath = out_dir+'/'+outFile_skewt
                        command = binDir+'/plot_skewt.py --inpath '+out_dir+' --infile '+base+'.new --outpath '+out_dir+' --fmt UWYO --hodo False --wb True --vlim 7'
                        print('skewt command =',command)
                        os.system(command)
                    
                        # Move skewt to field catalog directory if it exists
                        if os.path.exists(localSkewtPath):
                            sftp.put(localSkewtPath, sftpCatalogDestDir+'/'+outFile_skewt)
                
                        # ftp wetbulb plot to field catalog directory if it exists
                        # NOTE: Change code so figure header uses short_name instead of long_name
                        localWbPath = out_dir+'/'+outFile_wetbulb
                        if os.path.exists(localWbPath):
                            sftp.put(localWbPath, sftpCatalogDestDir+'/'+outFile_wetbulb)
                
                        # Close sftp connections
                        sftp.close()
                        ssh_client.close()
                
                        # Clean up
                        command = '/bin/rm '+base+'.txt '+base+'.new'
                        os.system(command)
                    
                        print('Done making skewt & wetbulb files')
