#!/bin/csh

if ($#argv != 2) then
  echo Usage: $0 infile outfile
  exit 1
endif

sed 's/<[^>]*>/\n/g'  $1 > $2

