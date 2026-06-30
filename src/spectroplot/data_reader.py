#!/usr/bin/python3

import sys                          #sys files processing
import re                           #regex
from pathlib import Path            #path processing (replace os)
from typing import Optional, Tuple
from spectroplot.global_constants import (
    specstring_start, specstring_end, ir_string,
)


class SpectrumData:
    """
    Object which will contain the spectrum data extracted from the
    orca.out/experiment.asc/orca.spectrum/orca.spectrum.rootX file.
    """

    def __init__(self, path: str) -> None:
        self.path: str = path
        self.name: str = self.read_name()
        self.filetype: str = self.read_ext()
        self.rootnumber: int = self.read_root()
        self.spectrum_type: str = ""
        self.data: list[list[float]] = self.read_data()

    def read_name(self) -> str:
        p = Path(self.path)
        #remove all suffixes to get the base name (handles multi-dot extensions)
        name = p.name[:-len(''.join(p.suffixes))] if p.suffixes else p.stem
        return name

    def read_ext(self) -> str:
        extlist = Path(self.path).suffixes
        ext = "".join(extlist)
        return ext

    def read_root(self) -> int:
        fext = self.filetype
        if re.search(r"\.spectrum\.root\d+$", fext):
            return int(next(re.finditer(r'\d+$', fext)).group(0))
        return 0

    def read_out_abs(self) -> Tuple[list[float], list[float]]:
        #check for uv data in orca.out
        found_uv_section = False
        energylist: list[float] = []       #energy cm-1
        intenslist: list[float] = []       #fosc
        with open(self.path, 'r') as file:
            for line in file:
                #detect ORCA version
                if "Program Version" in line:
                    version = re.search(r"\d\.\d\.\d", line)
                    if version and int(version[0][0]) < 6:
                        l1, l2 = 1, 3
                    else:
                        l1, l2 = 4, 7
                #start extract text
                if specstring_start in line:
                    #found UV data in orca.out
                    found_uv_section = True
                    for line in file:
                        if specstring_end in line:
                            #stop extract text
                            break
                        #only recognize lines that start with number
                        #split line into 3 lists mode, energy, intensities
                        #line should start with a number
                        if re.search(r"\d\s+\d", line):
                            energylist.append(float(line.strip().split()[l1]))
                            intenslist.append(float(line.strip().split()[l2]))
                    else:
                        continue    # executed if the inner loop didn't break
                    break           # executed if the inner loop did break

        #no UV data in orca.out -> exit here
        if not found_uv_section:
            print(f"'{specstring_start}' not found in '{self.path}'")
            sys.exit(1)

        #return data from orca.out
        return energylist, intenslist

    def read_ir(self) -> Tuple[list[float], list[float]]:
        freqlist: list[float] = []
        intenslist: list[float] = []
        with open(self.path, 'r') as file:
            for line in file:
                if ir_string in line:
                    for line in file:
                        if re.search(r"^\s*\d+:", line):
                            parts = line.strip().split()
                            freqlist.append(float(parts[1]))
                            intenslist.append(float(parts[3]))
                    break
        return freqlist, intenslist

    def read_out(self) -> Tuple[list[float], list[float]]:
        with open(self.path, 'r') as file:
            content = file.read()
        if ir_string in content:
            self.spectrum_type = "ir"
            return self.read_ir()
        self.spectrum_type = "tddft"
        return self.read_out_abs()

    def read_asc(self) -> Tuple[list[float], list[float]]:
        wavelengthlist: list[float] = []
        intenslist: list[float] = []
        with open(self.path, 'r') as file:
            for line in file:
                #start extract text
                wavelengthlist.append(float(line.strip().split()[0]))
                intenslist.append(float(line.strip().split()[1]))

        #return data from experiment.asc
        return wavelengthlist, intenslist

    def read_spectrum(self) -> Tuple[list[float], list[float]]:
        energylist: list[float] = []
        intenslist: list[float] = []
        with open(self.path, 'r') as file:
            for line in file:
                #start extract text
                if re.search(r"\d\s+\d", line):
                    energylist.append(float(line.strip().split()[0]))
                    intenslist.append(float(line.strip().split()[1]))

        #return data from experiment.asc
        return energylist, intenslist

    def read_data(self) -> list[list[float]]:
        fpath = self.path
        fext = self.filetype
        if fext == '.out':
            try:
                xlist, ylist = self.read_out()
            #file not found -> exit here
            except IOError:
                print(f"'{fpath}' not found")
                sys.exit(1)

        elif fext == '.asc':
            self.spectrum_type = "experimental"
            try:
                xlist, ylist = self.read_asc()
            #file not found -> exit here
            except IOError:
                print(f"'{fpath}' not found")
                sys.exit(1)

        elif fext == '.spectrum' or re.search(r"\.spectrum\.root\d+$", fext):
            self.spectrum_type = "esd"
            try:
                xlist, ylist = self.read_spectrum()
            #file not found -> exit here
            except IOError:
                print(f"'{fpath}' not found")
                sys.exit(1)

        else:
            print(f"Warning! The file {fpath} couldn't be opened.")
            sys.exit(1)

        return [xlist, ylist]

