"""Reader for ORCA output, experimental, and ESD spectrum files.

Created on January 10, 2026
@author: Emmanuel Bourret
"""

import logging
import re                           #regex

from pathlib import Path            #path processing (replace os)
from typing import Iterator, Optional, Tuple

from spectroplot.global_constants import (
    SPECSTRING_START, SPECSTRING_END, IR_STRING, VPT2_STRING,
    RAMAN_STRING,
)
from spectroplot._patterns import RE_SPECTRUM_ROOT

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SpectrumData:
    """Container for spectrum data extracted from an ORCA output file.

    Reads data from multiple file types:
    - ``.out`` : ORCA output (TD-DFT, IR, Raman, VPT2)
    - ``.asc`` : experimental data
    - ``.spectrum`` / ``.spectrum.rootX`` : ESD data

    Parameters
    ----------
    path : str
        Path to the spectrum file.

    Attributes
    ----------
    path : str
        Original file path.
    name : str
        Base name with all extensions stripped.
    filetype : str
        Full extension string.
    rootnumber : int
        ESD root number (0 if not an ESD root file).
    spectrum_type : str
        Type of spectrum (``"tddft"``, ``"ir"``, ``"raman"``,
        ``"vpt2"``, ``"experimental"``, or ``"esd"``).
    vpt2_nfund : int
        Number of VPT2 fundamental transitions (0 for non-VPT2).
    data : list of list of float
        Two-element list ``[xdata, ydata]``.
    """

    def __init__(self, path: str) -> None:
        self.path: str = path
        self.name: str = self.parse_name()
        self.filetype: str = self.read_ext()
        self.rootnumber: int = self.read_root()
        self.spectrum_type: str = ""
        self.vpt2_nfund: int = 0
        self.data: list[list[float]] = self.read_data()

    def parse_name(self) -> str:
        """Extract the base name by stripping all extensions.

        Returns
        -------
        str
            File name without any suffixes.
        """
        p = Path(self.path)
        name = p.name[:-len(''.join(p.suffixes))] if p.suffixes \
               else p.stem
        return name

    def read_ext(self) -> str:
        """Return the full extension string of the file.

        Returns
        -------
        str
            Concatenated suffixes (e.g. ``".spectrum.root1"``).
        """
        extlist = Path(self.path).suffixes
        ext = "".join(extlist)
        return ext

    def read_root(self) -> int:
        """Parse the ESD root number from the file extension.

        Returns
        -------
        int
            Root number, or 0 if the file is not an ESD root.
        """
        fext = self.filetype
        if RE_SPECTRUM_ROOT.search(fext):
            return int(next(re.finditer(r'\d+$', fext)).group(0))
        return 0

    def __repr__(self) -> str:
        return (
            f"SpectrumData(name={self.name!r}, type={self.filetype!r}, "
            f"spec_type={self.spectrum_type!r}, "
            f"root={self.rootnumber}, npts={len(self.data[0])})"
        )

    def read_out_abs(
        self, lines: Optional[list[str]] = None
    ) -> Tuple[list[float], list[float]]:
        """Extract absorption energies and oscillator strengths.

        Parameters
        ----------
        lines : list of str or None
            Pre-read file lines (avoids re-reading for sub-readers).

        Returns
        -------
        tuple of (list of float, list of float)
            Energies (cm⁻¹) and oscillator strengths.

        Raises
        ------
        ValueError
            If the ABSORPTION SPECTRUM section is not found.
        """
        found_uv_section = False
        energylist: list[float] = []
        intenslist: list[float] = []
        it: Iterator[str]
        if lines is not None:
            it = iter(lines)
        else:
            it = open(self.path, 'r')
        try:
            for line in it:
                if "Program Version" in line:
                    version = re.search(r"\d\.\d\.\d", line)
                    if version and int(
                        version[0].split(".")[0]
                    ) < 6:
                        l1, l2 = 1, 3
                    else:
                        l1, l2 = 4, 7
                if SPECSTRING_START in line:
                    found_uv_section = True
                    for line in it:
                        if SPECSTRING_END in line:
                            break
                        if re.search(r"^\s*\d+\s+\d", line):
                            energylist.append(
                                float(line.strip().split()[l1])
                            )
                            intenslist.append(
                                float(line.strip().split()[l2])
                            )
                    break
        finally:
            if lines is None:
                it.close()

        if not found_uv_section:
            raise ValueError(
                f"'{SPECSTRING_START}' not found in '{self.path}'"
            )

        return energylist, intenslist

    def read_ir(
        self, lines: Optional[list[str]] = None
    ) -> Tuple[list[float], list[float]]:
        """Extract IR frequencies and intensities.

        Parameters
        ----------
        lines : list of str or None
            Pre-read file lines.

        Returns
        -------
        tuple of (list of float, list of float)
            Frequencies (cm⁻¹) and intensities (km/mol).
        """
        freqlist: list[float] = []
        intenslist: list[float] = []
        it: Iterator[str]
        if lines is not None:
            it = iter(lines)
        else:
            it = open(self.path, 'r')
        try:
            for line in it:
                if IR_STRING in line:
                    seen_data = False
                    for line in it:
                        if not line.strip():
                            if seen_data:
                                break
                            continue
                        if re.search(r"^\s*\d+:", line):
                            parts = line.strip().split()
                            freqlist.append(float(parts[1]))
                            intenslist.append(float(parts[3]))
                            seen_data = True
                    break
        finally:
            if lines is None:
                it.close()
        return freqlist, intenslist

    def read_raman(
        self, lines: Optional[list[str]] = None
    ) -> Tuple[list[float], list[float]]:
        """Extract Raman frequencies and activities.

        Parameters
        ----------
        lines : list of str or None
            Pre-read file lines.

        Returns
        -------
        tuple of (list of float, list of float)
            Frequencies (cm⁻¹) and Raman activities.
        """
        freqlist: list[float] = []
        activlist: list[float] = []
        it: Iterator[str]
        if lines is not None:
            it = iter(lines)
        else:
            it = open(self.path, 'r')
        try:
            for line in it:
                if RAMAN_STRING in line:
                    seen_data = False
                    for line in it:
                        if not line.strip():
                            if seen_data:
                                break
                            continue
                        if re.search(r"^\s*\d+:", line):
                            parts = line.strip().split()
                            freqlist.append(float(parts[1]))
                            activlist.append(float(parts[2]))
                            seen_data = True
                    break
        finally:
            if lines is None:
                it.close()
        return freqlist, activlist

    def read_vpt2(
        self, lines: Optional[list[str]] = None
    ) -> Tuple[list[float], list[float]]:
        """Extract VPT2 anharmonic frequencies and intensities.

        Reads fundamental transitions, matches them to IR intensities
        by mode offset, and appends overtone / combination bands.

        Parameters
        ----------
        lines : list of str or None
            Pre-read file lines. If None the file is read once.

        Returns
        -------
        tuple of (list of float, list of float)
            Frequencies (cm⁻¹) and intensities.
        """
        freqlist: list[float] = []
        intenslist: list[float] = []

        if lines is None:
            with open(self.path, 'r') as file:
                lines = file.readlines()

        # 1. Parse "Fundamental transitions" table
        fund_start: Optional[int] = None
        for i, line in enumerate(lines):
            if 'Fundamental transitions' in line:
                fund_start = i
                break

        if fund_start is None:
            logger.warning("No VPT2 fundamental transitions found")
            return freqlist, intenslist

        fund_data: dict[int, float] = {}
        started = False
        for line in lines[fund_start + 1:]:
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    mode = int(parts[0])
                    v_fund = float(parts[2])
                    started = True
                    fund_data[mode] = v_fund
                except ValueError:
                    if started:
                        break
            elif started:
                break

        # 2. Parse last "IR Intensities" section
        ir_start: Optional[int] = None
        for i in range(len(lines) - 1, -1, -1):
            if 'IR Intensities' in lines[i]:
                ir_start = i
                break

        if ir_start is None:
            logger.warning("No IR Intensities found in VPT2 output")
            return freqlist, intenslist

        ir_intensities: dict[int, float] = {}
        started = False
        for line in lines[ir_start + 1:]:
            parts = line.strip().split()
            if len(parts) >= 7:
                try:
                    mode = int(parts[0])
                    intensity = float(parts[2])
                    started = True
                    ir_intensities[mode] = intensity
                except ValueError:
                    if started:
                        break
            elif started:
                break

        # 3. Match fundamental mode N with IR intensity at mode N+6
        self.vpt2_nfund = len(fund_data)
        for mode, v_fund in fund_data.items():
            ir_mode = mode + 6
            if ir_mode in ir_intensities:
                freqlist.append(v_fund)
                intenslist.append(ir_intensities[ir_mode])

        # 4. Parse "Overtones and combination bands"
        overt_start: Optional[int] = None
        for i, line in enumerate(lines):
            if 'Overtones and combination bands' in line:
                overt_start = i
                break

        if overt_start is not None:
            started = False
            for line in lines[overt_start + 1:]:
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split()
                if len(parts) >= 6:
                    try:
                        if parts[0].isdigit() and parts[1].isdigit():
                            freq = float(parts[2])
                            intensity = float(parts[4])
                            started = True
                            freqlist.append(freq)
                            intenslist.append(intensity)
                    except (ValueError, IndexError):
                        if started:
                            break
                elif started:
                    break

        return freqlist, intenslist

    def read_out(self) -> Tuple[list[float], list[float]]:
        """Read an ``.out`` file and dispatch to the correct parser.

        Detection priority: VPT2 → Raman → IR → TD-DFT.

        The file is read once and the content is reused to avoid
        repeated I/O.

        Returns
        -------
        tuple of (list of float, list of float)
            Energy and intensity data.
        """
        with open(self.path, 'r') as file:
            lines = file.readlines()
        content = ''.join(lines)
        if VPT2_STRING in content:
            self.spectrum_type = "vpt2"
            return self.read_vpt2(lines)
        if RAMAN_STRING in content:
            self.spectrum_type = "raman"
            return self.read_raman(lines)
        if IR_STRING in content:
            self.spectrum_type = "ir"
            return self.read_ir(lines)
        self.spectrum_type = "tddft"
        return self.read_out_abs(lines)

    def read_asc(self) -> Tuple[list[float], list[float]]:
        """Read experimental data from an ``.asc`` file.

        Each line is expected to contain at least two columns:
        wavelength and intensity.

        Returns
        -------
        tuple of (list of float, list of float)
            Wavelengths (nm) and intensities.
        """
        wavelengthlist: list[float] = []
        intenslist: list[float] = []
        with open(self.path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                try:
                    wavelengthlist.append(float(parts[0]))
                    intenslist.append(float(parts[1]))
                except ValueError:
                    continue

        return wavelengthlist, intenslist

    def read_spectrum(self) -> Tuple[list[float], list[float]]:
        """Read ESD data from a ``.spectrum`` or ``.spectrum.rootX`` file.

        Each line starting with a digit is parsed for energy and
        intensity values.

        Returns
        -------
        tuple of (list of float, list of float)
            Energies (cm⁻¹) and intensities.
        """
        energylist: list[float] = []
        intenslist: list[float] = []
        with open(self.path, 'r') as file:
            for line in file:
                if re.search(r"^\s*\d", line):
                    parts = line.strip().split()
                    if len(parts) < 2:
                        continue
                    try:
                        energylist.append(float(parts[0]))
                        intenslist.append(float(parts[1]))
                    except ValueError:
                        continue

        return energylist, intenslist

    def read_data(self) -> list[list[float]]:
        """Route the file to the correct reader based on extension.

        Returns
        -------
        list of list of float
            Two-element list ``[xdata, ydata]``.

        Raises
        ------
        ValueError
            If the file extension is not recognised.
        """
        fpath = self.path
        fext = self.filetype
        if fext == '.out':
            xlist, ylist = self.read_out()
        elif fext == '.asc':
            self.spectrum_type = "experimental"
            xlist, ylist = self.read_asc()
        elif fext == '.spectrum' or RE_SPECTRUM_ROOT.search(fext):
            self.spectrum_type = "esd"
            xlist, ylist = self.read_spectrum()
        else:
            raise ValueError(
                f"Unknown file extension '{fext}' for file '{fpath}'"
            )

        return [xlist, ylist]
