#!/usr/bin/python3
import sys
import os
import re
import argparse
import numpy as np

#global variables
header="Energy       TotalSpectrum      IntensityFC        IntensityHT"

#global lists
energylist_tot=list()       #energy cm-1 from ESD
intenslist_tot=list()       #total spectrum from ESD
fclist_tot=list()           #FC intensities from ESD
htlist_tot=list()           #HT intensities from ESD

#create parser
parser = argparse.ArgumentParser(prog='sum_spectra',\
    description='Easily sum absorption spectra from ORCA ESD module')

#file is required
parser.add_argument("filename",
    nargs='+',
    help="the ORCA ESD output file")

#parse arguments
args = parser.parse_args()


for index,path in enumerate(args.filename):
    filename_root=path
    energylist=list()
    intenslist=list()
    fclist=list()
    htlist=list()
    try:
        with open(filename_root, "r") as input_file:
            for line in input_file:
                #start extract text
                if re.search("\d\s{1,}\d",line):
                    energylist.append(float(line.strip().split()[0]))
                    intenslist.append(float(line.strip().split()[1]))
                    fclist.append(float(line.strip().split()[2]))
                    htlist.append(float(line.strip().split()[3]))
        
        print("{0:s}\t{1:e}".format(filename_root,max(intenslist)))
        energylist_tot = energylist
        if index == 0:
            intenslist_tot = intenslist
            fclist_tot = fclist
            htlist_tot = htlist
            fname, fext = os.path.splitext(path)
        else:
            intenslist_tot = np.add(intenslist_tot,intenslist)
            fclist_tot = np.add(fclist_tot,fclist)
            htlist_tot = np.add(htlist_tot,htlist)

    #file not found -> exit here
    except IOError:
        print(f"'{filename}'" + " not found")
        sys.exit(1)

data = np.column_stack([energylist_tot, intenslist_tot, fclist_tot, htlist_tot])
np.savetxt(fname, data, fmt=['%.2f','%18.6e','%18.6e','%18.6e'],
        header=header,comments='')
