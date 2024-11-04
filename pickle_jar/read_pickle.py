#!/usr/bin/python3

import pandas as pd

pickleDir = '/home/disk/bob/s2noclime/bin/pickle_jar'
pickleFile = 'asos_co.pkl'

asos_co = pd.read_pickle(pickleDir+'/'+pickleFile)

## Compare to 2020 data to see if data is the same -- it is
#pickleFile = 'nysm.pkl'
#site_info_2020 = pd.read_pickle(pickleDir+'/'+pickleFile)
#site_info_2020.equals(site_info_2021)
