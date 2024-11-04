#!/usr/bin/python

import sys

def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

if len(sys.argv) != 3:
    raise SystemExit("Useage: {} {} {}".format(sys.argv[0], "[infile]", "[outfile]"))
inFile = sys.argv[1]
outFile = sys.argv[2]

f_in = open(inFile,'r')
f_out = open(outFile,'w')

# skip first 18 lines
for i in range(0,18):
    header = f_in.readline()
    f_out.write(header)

for line in f_in:
    columns = line.split()
    ncolumns = len(columns)
    if ncolumns > 0:
        if is_number(columns[0]):
            if ncolumns == 11:
                f_out.write(line)
        else:
            f_out.write(line)
    else:
        f_out.write(line)

f_in.close()
f_out.close()


