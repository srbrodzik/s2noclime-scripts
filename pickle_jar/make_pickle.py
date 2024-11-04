#!/usr/bin/python3

import pickle
import pandas as pd
import sys

if len(sys.argv) != 2:
    print('Usage: '+sys.argv[0]+' fileType[asos]')
    sys.exit()
else:
    fileType = sys.argv[1]

if fileType == 'asos':

    csvDir = '/home/disk/bob/s2noclime/bin/pickle_jar'
    csvFile = 'asos-stations-s2noclime.txt'
    pickleDir = '/home/disk/bob/s2noclime/bin/pickle_jar'
    pickleFile = 'asos_s2noclime.pkl'

    # Read csv file into DataFrame
    use_cols = ["CALL","NAME","ST","LAT","LON","ELEV"]
    df = pd.read_fwf(csvDir+'/'+csvFile, usecols=use_cols,
                     widths=[9,6,7,5,31,31,21,3,31,10,11,7,6,51,9,12,7,7])
    
    # Remove rows where callsign is NaN
    df.dropna(subset=['CALL'],inplace=True)
    #index = range(len(df))
    #df = pd.DataFrame(df,index)

    # Append 'K' to call signs
    for i in df.index:
        print(df.loc[i,'CALL'])
        if len(df.loc[i,'CALL']) > 3:
            df.drop(axis=0,index=i,inplace=True)
        else:
            df.at[i,'CALL'] = 'K'+df.loc[i,'CALL']
            
    # Change index to CALL
    df.set_index('CALL',inplace=True)
    
    # Pickle DataFrame
    df.to_pickle(pickleDir+'/'+pickleFile)

else:
    print('fileType = ',fileType,' not recognized.')

    
