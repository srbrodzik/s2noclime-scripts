#!/usr/bin/python3

import os 
import pandas as pd
from io import StringIO 
import json            #javascript object notation encoder and decoder
import urllib 
import urllib.parse
import urllib.request
import math
import csv 
import time, datetime
from time import strftime 
from datetime import datetime
from datetime import timedelta
import numpy as np 
import matplotlib 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt 
import pickle

# Inputs
SECS_IN_MIN = 60
MINS_IN_HOUR = 60
HRS_IN_DAY = 24
missingValue = -999.

# ARCHIVE MODE
#start_date = '20211229'
#stop_date  = '20220121'

# REALTIME MODE
now = datetime.utcnow()
twelve_hrs_ago = now - timedelta(hours=12)
start_date = twelve_hrs_ago.strftime("%Y%m%d")
stop_date = now.strftime("%Y%m%d")

csv_dir = '/home/disk/bob/s2noclime/raw/asos_isu'

# Get sitelist
pickle_jar = '/home/disk/bob/s2noclime/bin/pickle_jar/'
infile = open(pickle_jar + "asos_s2noclime.pkl",'rb')
siteinfo = pickle.load(infile)
infile.close()
sitelist = siteinfo.index
# FOR TESTING
#sitelist = ['KLXV']

# Determine datelist
start_date_obj = datetime.strptime(start_date,'%Y%m%d')
stop_date_obj = datetime.strptime(stop_date,'%Y%m%d')
total_days = int( (stop_date_obj - start_date_obj).total_seconds() / SECS_IN_MIN / MINS_IN_HOUR / HRS_IN_DAY ) + 1
datelist = []
for i in range(0,total_days):
    new_date_obj = start_date_obj + timedelta(days=i)
    new_date_str = new_date_obj.strftime('%Y%m%d')
    datelist.append( new_date_str  )
#FOR TESTING
#datelist = ['20221127','20221126']

def load_and_save_station_data(site):
    '''Given a site station ID, returns 3-day DataFrame of specified weather variables. Also saves a each day's
    worth of data for the last three days into a .csv file for that station, within a folder for that day. 
    
    Parameters:
    site (str): string of ASOS station ID
    
    Returns: 
    df (dataframe): dataframe containing last 72 hours (3 days) of ASOS station data 
    
    *Saves .csv files to csv_dir listed near top of script*
    '''

    lower_site = site.lower()

    #definining dates in YYYYmmdd format (for saving and finding files)
    today_date = date  # string
    today_dt_obj = datetime.strptime(today_date,'%Y%m%d') # datetime object
    tomorrow_dt_obj = today_dt_obj + timedelta(days=1)
    year1 = today_dt_obj.strftime('%Y')
    month1 = today_dt_obj.strftime('%m')
    day1 = today_dt_obj.strftime('%d')
    year2 = tomorrow_dt_obj.strftime('%Y')
    month2 = tomorrow_dt_obj.strftime('%m')
    day2 = tomorrow_dt_obj.strftime('%d')
    today_date_dt_format = today_dt_obj.strftime('%Y-%m-%d')  # YYYY-mm-dd format
    
    path0_dir = csv_dir+'/'+today_date
    if not os.path.isdir(path0_dir):
        os.makedirs(path0_dir)
        
    path0_file = path0_dir+'/S2NOCLIME_ASOS_'+today_date+'_'+lower_site+'.csv'
    
    # Use ISU interface
    args=[('station',site), ('data','tmpc'), ('data','dwpc'),
          ('data','drct'), ('data','sknt'), ('data','mslp'), 
          ('data','p01m'), ('data','gust'), ('data','wxcodes'), 
          ('year1',year1), ('month1',month1), ('day1',day1),
          ('year2',year2), ('month2',month2), ('day2',day2), 
          ('tz','UTC'), ('format','onlycomma'), ('latlon','no'),
          ('missing','empty'), ('trace','empty'), ('direct','no'),
          ('report_type','1'), ('report_type','2')]

    apiString = urllib.parse.urlencode(args)
    url = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
    fullUrl = '{}?{}'.format(url,apiString)
    response = urllib.request.urlopen(fullUrl).read()
    response_string = str(response,'utf-8')
    response_data = StringIO(response_string) 
    new_data = pd.read_csv(response_data,sep=',')

    # Check for no data
    if len(new_data) == 0: 
        print("Problem reading data for %s. Data was not updated" % site)
        return 0

    # Rename 'valid' column name to 'time'
    #new_data.rename(columns={'valid':'date_time'}, inplace=True)
    new_data.rename(columns={'valid':'time'}, inplace=True)
    
    # Convert date_time strings to datetime objects
    #new_data['date_time'] = pd.to_datetime(new_data['date_time'])
    new_data['time'] = pd.to_datetime(new_data['time'])
    
    # Set time as index
    #new_data.set_index('date_time',inplace=True)
    new_data.set_index('time',inplace=True)

    # Standaradize the format of all the ASOS csv files
    try: 
        new_data = new_data[['tmpc','dwpc','drct','sknt','gust','mslp','p01m','wxcodes']]
    #Catches non reported fields and enters a set of "NaNs" in their place                    
    except KeyError as keyErr:

        #Edits the key error into a string which has only the missing fields with spaces inbetween
        keyErr = str(keyErr)[3:].replace("] not in index\"","")
        keyErr = keyErr.replace("\'","")
        keyErr = keyErr.replace("\\n","")

        #Splits the missing fields into a list
        missing_items = keyErr.split()
        for item in missing_items: #Adds a column of NaNs corrected for the length of the data
            new_data[item] = [float('NaN') for x in np.arange(new_data.shape[0])] 
        #Standardizes the format
        new_data = new_data[['tmpc','dwpc','drct','sknt','gust','mslp','p01m','wxcodes']]
    
    # Save data to csv file
    data = new_data[today_date_dt_format]
    data = data.sort_index()
    data.to_csv(path0_file)

for date in datelist:
    for i,site in enumerate(sitelist):
        print(date,site)
        #df = load_and_save_station_data(site)
        load_and_save_station_data(site)
