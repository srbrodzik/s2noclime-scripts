#!/bin/csh

source /home/disk/meso-home/meso/.cshrc
setenv MDV_WRITE_FORMAT FORMAT_NCF 
exec /home/disk/bob/s2noclime/bin/run.MrmsGribIngestRhoHV_v2.py
