#!/usr/bin/python3

import sys                          #sys files processing
import re                           #regex
from pathlib import Path            #path processing (replace os)
from global_constants import specstring_start, specstring_end

class SpectrumData(object):
    """
    Object which will contain the spectrum data extracted from the
    orca.out/experiment.asc/orca.spectrum/orca.spectrum.rootX file.
    """

    def __init__(self,path):

        self.path = path
        self.name = self.read_name()
        self.filetype = self.read_ext()
        self.rootnumber = self.read_root()
        self.data = self.read_data()


    def read_name(self):
        name = Path(Path(self.path).stem).stem
        return name

    def read_ext(self):
        extlist = Path(self.path).suffixes
        ext = "".join(extlist)
        return ext

    def read_root(self):
        fext = self.filetype
        if re.search(".spectrum.root\d+",fext):
            return int(next(re.finditer(r'\d+$',fext)).group(0))
        else:
            return int(0)

    def read_out(self):
        #check for uv data in orca.out
        found_uv_section=False
        energylist=list()       #energy cm-1
        intenslist=list()       #fosc
        with open(self.path,'r') as file:
            for line in file:
                #detect ORCA version
                if "Program Version" in line:
                    version=re.search("\d\.\d\.\d",line)[0]
                    if int(version[0]) < 6:
                        l1,l2=1,3
                    else:
                        l1,l2=4,7
                #start extract text
                if specstring_start in line:
                    #found UV data in orca.out
                    found_uv_section=True
                    for line in file:
                        if specstring_end in line:
                            #stop extract text
                            break
                        #only recognize lines that start with number
                        #split line into 3 lists mode, energy, intensities
                        #line should start with a number
                        if re.search("\d\s+\d",line):
                            energylist.append(float(line.strip().split()[l1]))
                            intenslist.append(float(line.strip().split()[l2]))
                    else:
                        continue    # executed if the inner loop didn't break
                    break           # executed if the inner loop did break

        #no UV data in orca.out -> exit here
        if not found_uv_section:
            print(f"'{specstring_start}'" + "not found in" +f"'{self.path}'")
            sys.exit(1)

        #return data from orca.out
        return energylist,intenslist

    def read_asc(self):
        wavelengthlist=list()
        intenslist=list()
        with open(self.path,'r') as file:
            for line in file:
                #start extract text
                wavelengthlist.append(float(line.strip().split()[0]))
                intenslist.append(float(line.strip().split()[1]))

        #return data from experiment.asc
        return wavelengthlist,intenslist

    def read_spectrum(self):
        energylist=list()
        intenslist=list()
        with open(self.path,'r') as file:
            for line in file:
                #start extract text
                if re.search("\d\s+\d",line):
                    energylist.append(float(line.strip().split()[0]))
                    intenslist.append(float(line.strip().split()[1]))

        #return data from experiment.asc
        return energylist,intenslist

    def read_data(self):
        fpath = self.path
        fext = self.filetype
        if fext == '.out':
            try:
                xlist,ylist = self.read_out()
            #file not found -> exit here
            except IOError:
                print(f"'{fpath}'" + " not found")
                sys.exit(1)

        elif fext == '.asc':
            try:
                xlist,ylist = self.read_asc()
            #file not found -> exit here
            except IOError:
                print(f"'{fpath}'" + " not found")
                sys.exit(1)

        elif fext == '.spectrum' or re.search(".spectrum.root\d+",fext):
            try:
                xlist,ylist = self.read_spectrum()
            #file not found -> exit here
            except IOError:
                print(f"'{fpath}'" + " not found")
                sys.exit(1)

        else:
            print(r"warning! The file %s couldn't be opened." % fpath)
            sys.exit(1)

        return [xlist,ylist]

