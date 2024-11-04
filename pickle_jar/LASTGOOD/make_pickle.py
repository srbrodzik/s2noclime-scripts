#!/usr/bin/python3

import pickle
import pandas as pd
import sys

if len(sys.argv) != 2:
    print('Usage: '+sys.argv[0]+' fileType[ground/swe/profiler]')
    sys.exit()
else:
    fileType = sys.argv[1]

if fileType == 'ground':

    csvDir = '/home/disk/bob/impacts/raw/nys_ground_2021/csv'
    csvFile = 'nysm.csv'
    pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'
    pickleFile = 'nysm_2021.pkl'

    # Read csv file into DataFrame
    df = pd.read_csv (csvDir+'/'+csvFile)

    # Pickle DataFrame
    df.to_pickle(pickleDir+'/'+pickleFile)

    #array(['stid', 'number', 'name', 'lat [degrees]', 'lon [degrees]',
    #       'elevation [m]', 'county', 'nearest_city', 'state',
    #       'distance_from_town [km]', 'direction_from_town [degrees]',
    #       'climate_division', 'climate_division_name', 'wfo', 'commissioned',
    #       'decommissioned'], dtype=object)

elif fileType == 'swe':
    
    csvDir = '/home/disk/bob/impacts/raw/nys_swe_2021/csv'
    csvFile = 'snow.csv'
    pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'
    pickleFile = 'nysm_swe_2021.pkl'

    # Read csv file into DataFrame
    df = pd.read_csv (csvDir+'/'+csvFile)

    # Pickle DataFrame
    df.to_pickle(pickleDir+'/'+pickleFile)

    #array(['stid','fname','time','recNum','int_end_time','network',
    #       'serialNum','K_cnts_uncorr','K_cnts_corr','Tl_cnts_corr',
    #       'swe_from_K','swe_from_K_Tl','swe_from_Tl','soil_moisture_from_K',
    #       'soil_moisture_from_Tl','soil_moisture_from_K_Tl','precip_index',
    #       'crystal_temp_min','crystal_temp_max','total_hist_blocks_used',
    #       'K_peak_displacement','stat_signif_swe_Tl','power_input_voltage'],
    #      dtype=objext)

else:
    print('fileType = ',fileType,' not recognized.')

    
