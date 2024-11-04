#!/usr/bin/python3

import sys
import os
import netCDF4 as nc
import shutil
from datetime import datetime
from datetime import date
from datetime import timezone
import glob

gribDir = '/home/disk/bob/s2noclime/raw/mrms/2DCompRefl'
filePrefix = 'MRMS_MergedReflectivityQCComposite'
extension = 'grib2'
ncDirBase = '/home/disk/bob/s2noclime/netcdf/mrms/2DCompRefl'
mdvDirBase = '/home/disk/bob/s2noclime/mdv/mrms/2DCompRefl'
paramsDir = '/home/disk/bob/s2noclime/git/lrose-s2noclime/projDir/ingest/params'
ncVarName = 'DBZ_comp'
domain = ['33.','-130.','47.','-102.']   # [minLat,minLon,maxLat,maxLon]

for date in os.listdir(gribDir):
    if date.startswith('202') and os.path.isdir(gribDir+'/'+date):
        dateDir = gribDir+'/'+date

        for gribFile in os.listdir(dateDir):
            # get date/time info from filename
            (base,ext) = os.path.splitext(gribFile)
            [mrms,product,level,dateAndTime] = base.split('_')
            #dt_obj = datetime.strptime(dateAndTime, "%Y%m%d-%H%M%S")
            [junk,time] = dateAndTime.split('-')
    
            # convert grib2 to netcdf
            ncDir = ncDirBase+'/'+date
            ncFile = mrms+'.'+product+'.'+date+'.'+time+'.nc'

            if  not os.path.isdir(ncDir):
                os.makedirs(ncDir)
            command = 'wgrib2 '+dateDir+'/'+gribFile+' -netcdf '+ncDir+'/'+ncFile
            os.system(command)
            # Got this error when running as meso@bob:
            #/home/disk/sys/local/linux64/bin/wgrib2_stretch: error while loading shared libraries: libnetcdf.so.11: cannot open shared object file: No such file or directory

            # change variable name from MergedBaseReflectivityQC_500mabovemeansealevel to DBZ_base
            os.chdir(ncDir)
            ncFileNew = ncFile+'.new'
            command = 'ncrename -h -v MergedReflectivityQCComposite_500mabovemeansealevel,'+ncVarName+' '+ncFile+' '+ncFileNew
            os.system(command)
            shutil.move(ncFileNew,ncFile)

            # change base_refl attributes
            #command = 'ncatted -O -h -a short_name,base_refl,o,c,base_refl '+ncFileNew
            #os.system(command)
            #command = 'ncatted -O -h -a _FillValue,base_refl,o,f,-99 '+ncFileNew
            #os.system(command)

            # change all base_refl values < 0 to -999
            #with nc.Dataset(ncFileNew) as src:
            #    for varName, varIn in src.variables.items():
            #        if 'base_refl' in varName:
            #            base_refl = src[varName][:]
            #            base_refl[base_refl<0] = -999
            #            src[varName][:] = base_refl

            # add alt dim to ncFile
            # tcsh command line syntax:
            #ncap2 -s 'defdim("altitude",1);altitude[altitude]=0.5;altitude@long_name="altitude";altitude@units="km"' -O MRMS.MergedBaseReflectivityQC.20211215.224819.nc MRMS.MergedBaseReflectivityQC.20211215.224819_new.nc
            command = "ncap2 -s \'defdim(\"altitude\",1);altitude[altitude]=0.5;altitude@long_name=\"altitude\";altitude@units=\"km\"\' -O "+ncFile+" "+ncFileNew
            os.system(command)
            shutil.move(ncFileNew,ncFile)

            # change domain to S2noCliME region
            command = 'ncea -h -d latitude,'+domain[0]+','+domain[2]+' -d longitude,'+domain[1]+','+domain[3]+' '+ncFile+' '+ncFileNew
            os.system(command)
            shutil.move(ncFileNew,ncFile)

            # set DATE environment var
            os.environ['DATE'] = date
            command = 'NcGeneric2Mdv -v -params '+paramsDir+'/NcGeneric2Mdv.mrms_comp_refl -f '+ncFile
            os.system(command)

