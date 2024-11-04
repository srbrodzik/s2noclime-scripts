#!/usr/bin/python3

import os
import datetime
from datetime import date
from datetime import timezone
import glob

baseDir = '/home/disk/data/nexrad/mrms/3DZdr'
filePrefix = 'MRMS_MergedZdr'
extension = 'grib2'
topLevel = '19.00'
paramDir = '/home/disk/bob/s2noclime/git/lrose-s2noclime/projDir/ingest/params'

dt = datetime.datetime.now(timezone.utc)
date = dt.strftime("%Y%m%d")
hour = dt.strftime("%H")
minute = dt.strftime("%M")
dateDir = baseDir+'/'+date

files_topLevel = sorted(glob.glob(dateDir+'/'+filePrefix+'_'+topLevel+'_*'+extension))
file = os.path.basename(files_topLevel[-1])
(base,ext) = os.path.splitext(file)
dateTimeStr = base.replace(filePrefix+'_'+topLevel+'_','')
files_current = sorted(glob.glob(dateDir+'/'+filePrefix+'_*_'+dateTimeStr+ext))

if len(files_current) == 33:
    command = 'MrmsGribIngest -v -params '+paramDir+'/MrmsGribIngest.zdr -f '+dateDir+'/*'+dateTimeStr+ext
    os.system(command)
