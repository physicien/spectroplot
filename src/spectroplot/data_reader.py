import logging
import re                           #regex

logger = logging.getLogger(__name__)
from pathlib import Path            #path processing (replace os)
from typing import Optional, Tuple
from spectroplot.global_constants import (
    specstring_start, specstring_end, ir_string, vpt2_string,
    raman_string,
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
        self.vpt2_nfund: int = 0
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

    def __repr__(self) -> str:
        return (f"SpectrumData(name={self.name!r}, type={self.filetype!r}, "
                f"spec_type={self.spectrum_type!r}, "
                f"root={self.rootnumber}, npts={len(self.data[0])})")

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
                        if re.search(r"^\s*\d+\s+\d", line):
                            energylist.append(float(line.strip().split()[l1]))
                            intenslist.append(float(line.strip().split()[l2]))
                    else:
                        continue    # executed if the inner loop didn't break
                    break           # executed if the inner loop did break

        #no UV data in orca.out
        if not found_uv_section:
            raise ValueError(
                f"'{specstring_start}' not found in '{self.path}'"
            )

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

    def read_raman(self) -> Tuple[list[float], list[float]]:
        freqlist: list[float] = []
        activlist: list[float] = []
        with open(self.path, 'r') as file:
            for line in file:
                if raman_string in line:
                    for line in file:
                        if re.search(r"^\s*\d+:", line):
                            parts = line.strip().split()
                            freqlist.append(float(parts[1]))
                            activlist.append(float(parts[2]))
                    break
        return freqlist, activlist

    def read_vpt2(self) -> Tuple[list[float], list[float]]:
        freqlist: list[float] = []
        intenslist: list[float] = []

        with open(self.path, 'r') as file:
            lines = file.readlines()

        # 1. Parse "Fundamental transitions" table for anharmonic frequencies
        fund_start: Optional[int] = None
        for i, line in enumerate(lines):
            if 'Fundamental transitions' in line:
                fund_start = i
                break

        if fund_start is None:
            logger.warning("No VPT2 fundamental transitions found")
            return freqlist, intenslist

        fund_data: dict[int, float] = {}
        for line in lines[fund_start + 4:]:
            if line.strip().startswith('---'):
                break
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    mode = int(parts[0])
                    v_fund = float(parts[2])
                    fund_data[mode] = v_fund
                except ValueError:
                    continue

        # 2. Parse last "IR Intensities" section for intensities
        ir_start: Optional[int] = None
        for i in range(len(lines) - 1, -1, -1):
            if 'IR Intensities' in lines[i]:
                ir_start = i
                break

        if ir_start is None:
            logger.warning("No IR Intensities found in VPT2 output")
            return freqlist, intenslist

        ir_intensities: dict[int, float] = {}
        for line in lines[ir_start + 5:]:
            stripped = line.strip()
            if not stripped or stripped.startswith('-') \
                    or stripped.startswith('Calculate'):
                break
            parts = stripped.split()
            if len(parts) >= 7:
                try:
                    mode = int(parts[0])
                    intensity = float(parts[2])
                    ir_intensities[mode] = intensity
                except ValueError:
                    continue

        # 3. Match fundamental mode N with IR intensity at mode N+6
        self.vpt2_nfund = len(fund_data)
        for mode, v_fund in fund_data.items():
            ir_mode = mode + 6
            if ir_mode in ir_intensities:
                freqlist.append(v_fund)
                intenslist.append(ir_intensities[ir_mode])

        # 4. Parse "Overtones and combination bands" section
        overt_start: Optional[int] = None
        for i, line in enumerate(lines):
            if 'Overtones and combination bands' in line:
                overt_start = i
                break

        if overt_start is not None:
            for line in lines[overt_start + 4:]:
                stripped = line.strip()
                if not stripped or stripped.startswith('='):
                    break
                parts = stripped.split()
                if len(parts) >= 6:
                    try:
                        if parts[0].isdigit() and parts[1].isdigit():
                            freq = float(parts[2])
                            intensity = float(parts[4])
                            freqlist.append(freq)
                            intenslist.append(intensity)
                    except (ValueError, IndexError):
                        continue

        return freqlist, intenslist

    def read_out(self) -> Tuple[list[float], list[float]]:
        with open(self.path, 'r') as file:
            content = file.read()
        if vpt2_string in content:
            self.spectrum_type = "vpt2"
            return self.read_vpt2()
        if raman_string in content:
            self.spectrum_type = "raman"
            return self.read_raman()
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
                if re.search(r"^\s*\d", line):
                    energylist.append(float(line.strip().split()[0]))
                    intenslist.append(float(line.strip().split()[1]))

        #return data from experiment.asc
        return energylist, intenslist

    def read_data(self) -> list[list[float]]:
        fpath = self.path
        fext = self.filetype
        if fext == '.out':
            xlist, ylist = self.read_out()
        elif fext == '.asc':
            self.spectrum_type = "experimental"
            xlist, ylist = self.read_asc()
        elif fext == '.spectrum' or re.search(r"\.spectrum\.root\d+$", fext):
            self.spectrum_type = "esd"
            xlist, ylist = self.read_spectrum()
        else:
            raise ValueError(
                f"Unknown file extension '{fext}' for file '{fpath}'"
            )

        return [xlist, ylist]

