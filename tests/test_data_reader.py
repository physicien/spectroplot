import sys
sys.path.insert(0, "src")

from spectroplot.data_reader import SpectrumData
from spectroplot.global_constants import specstring_start, specstring_end


DATA_DIR = "data"


class TestSpectrumDataAsc:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/experimental/C60.asc")

    def test_filetype(self):
        assert self.sd.filetype == ".asc"

    def test_name(self):
        assert self.sd.name == "C60"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) > 0

    def test_spectrum_type(self):
        assert self.sd.spectrum_type == "experimental"

    def test_data_ranges(self):
        x, y = self.sd.data
        assert all(isinstance(v, float) for v in x)
        assert all(isinstance(v, float) for v in y)
        assert x[0] > x[-1]  # wavelengths descending


class TestSpectrumDataSpectrum:
    def setup_method(self):
        self.sd = SpectrumData(
            f"{DATA_DIR}/ESD/FLUOR/lw100/FLUOR_c60-Ih_esd.spectrum"
        )

    def test_filetype(self):
        assert self.sd.filetype == ".spectrum"

    def test_name(self):
        assert self.sd.name == "FLUOR_c60-Ih_esd"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

    def test_spectrum_type(self):
        assert self.sd.spectrum_type == "esd"

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) > 0

    def test_first_values(self):
        x, y = self.sd.data
        assert abs(x[0] - 5001.415505) < 1e-6
        assert abs(y[0] - 1.200954e02) < 1e-3


class TestSpectrumDataOut:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/TD-DFT/UV_c60-Ih.out")

    def test_filetype(self):
        assert self.sd.filetype == ".out"

    def test_name(self):
        assert self.sd.name == "UV_c60-Ih"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

    def test_spectrum_type(self):
        assert self.sd.spectrum_type == "tddft"

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) > 0

    def test_energy_and_fosc_positive(self):
        x, y = self.sd.data
        assert all(e > 0 for e in x)
        assert all(f >= 0 for f in y)


class TestSpectrumDataRoot:
    def setup_method(self):
        self.sd = SpectrumData(
            f"{DATA_DIR}/ESD/ABS/ABS_pyrene_esd.spectrum.root1"
        )

    def test_filetype(self):
        assert self.sd.filetype == ".spectrum.root1"

    def test_name(self):
        assert self.sd.name == "ABS_pyrene_esd"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 1

    def test_spectrum_type(self):
        assert self.sd.spectrum_type == "esd"

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) > 0

    def test_first_values(self):
        x, y = self.sd.data
        assert abs(x[0] - 10002.83) < 1e-2
        assert abs(y[0] - 5.291294e-01) < 1e-6


class TestSpectrumDataIR:
    def setup_method(self):
        self.sd = SpectrumData(
            f"{DATA_DIR}/IR/FRQ_tungsten_hexacarbonyl_f.out"
        )

    def test_filetype(self):
        assert self.sd.filetype == ".out"

    def test_name(self):
        assert self.sd.name == "FRQ_tungsten_hexacarbonyl_f"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

    def test_spectrum_type(self):
        assert self.sd.spectrum_type == "ir"

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) > 0

    def test_first_values(self):
        x, y = self.sd.data
        assert abs(x[0] - 61.13) < 1e-2
        assert abs(y[0] - 0.00) < 1e-6


class TestSpectrumDataVPT2:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/VPT2/VPT2_furan_vpt2.out")

    def test_filetype(self):
        assert self.sd.filetype == ".out"

    def test_name(self):
        assert self.sd.name == "VPT2_furan_vpt2"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

    def test_spectrum_type(self):
        assert self.sd.spectrum_type == "vpt2"

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) == 252

    def test_first_fundamental(self):
        x, y = self.sd.data
        assert abs(x[0] - 601.909) < 1e-3
        assert abs(y[0] - 0.000) < 1e-3

    def test_second_fundamental(self):
        x, y = self.sd.data
        assert abs(x[1] - 619.255) < 1e-3
        assert abs(y[1] - 21.056) < 1e-3

    def test_first_overtone(self):
        x, y = self.sd.data
        assert abs(x[21] - 1204.60) < 1e-2
        assert abs(y[21] - 0.01) < 1e-2


class TestSpectrumDataRaman:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/Raman/RAM_c60-Ih_r.out")

    def test_filetype(self):
        assert self.sd.filetype == ".out"

    def test_name(self):
        assert self.sd.name == "RAM_c60-Ih_r"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

    def test_spectrum_type(self):
        assert self.sd.spectrum_type == "raman"

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) == 174

    def test_first_values(self):
        x, y = self.sd.data
        assert abs(x[0] - 257.02) < 1e-2
        assert abs(y[0] - 25.589899) < 1e-6

    def test_most_intense(self):
        x, y = self.sd.data
        i_max = max(range(len(y)), key=lambda i: y[i])
        assert abs(x[i_max] - 1475.87) < 1e-2
        assert abs(y[i_max] - 378.715279) < 1e-6


# Isolation tests for .out sub-readers
IR_LINES = [
    "some header\n",
    "IR SPECTRUM\n",
    "-------------\n",
    "\n",
    " Mode    freq (cm**-1)   epsilon   Int\n",
    "-------------------------------------------\n",
    "    1:     100.00       0.001    0.500000\n",
    "    2:     200.00       0.002    0.300000\n",
    "    3:     300.00       0.003    0.100000\n",
    "\n",
    "other data\n",
]

RAMAN_LINES = [
    "some header\n",
    "RAMAN SPECTRUM\n",
    "----------------\n",
    "\n",
    " Mode    freq (cm**-1)   Activity   Depolarization\n",
    "---------------------------------------------------------\n",
    "    1:     100.00      0.500000      0.750000\n",
    "    2:     200.00      0.300000      0.250000\n",
    "    3:     300.00      0.100000      0.500000\n",
    "\n",
    "other data\n",
]

VPT2_LINES = [
    "some header\n",
    "Fundamental transitions\n",
    "-----------------------------------------\n",
    "Mode   w(har)  v(fund)  Diff\n",
    "-----------------------------------------\n",
    "1      500.0   490.0   -10.0\n",
    "2      600.0   595.0    -5.0\n",
    "---\n",
    "IR Intensities\n",
    "-----------------------------------------------------------------\n",
    "\n",
    "Mode freq     Int          T2   (      Tx       Ty       Tz     )\n",
    "-----------------------------------------------------------------\n",
    "7    500.0   10.0      0.005     ( 0.1       0.2       0.3)\n",
    "8    600.0   20.0      0.010     ( 0.3       0.4       0.5)\n",
    "Calculate...\n",
    "Overtones and combination bands\n",
    "-------------------------------\n",
    "\n",
    "modes   freq    eps       Int       T**2      (Tx Ty Tz)\n",
    "---------------------------------------------------------\n",
    "1 1    980.0   0.01      5.0       0.002     (0.1 0.2 0.3)\n",
    "2 2   1190.0   0.02      3.0       0.001     (0.3 0.4 0.5)\n",
    "==============================\n",
    "other data\n",
]


class TestReadIrIsolation:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/TD-DFT/UV_c60-Ih.out")

    def test_read_ir_lines(self):
        x, y = self.sd.read_ir(lines=IR_LINES)
        assert len(x) == 3
        assert abs(x[0] - 100.0) < 1e-6
        assert abs(y[0] - 0.5) < 1e-6
        assert abs(x[2] - 300.0) < 1e-6

    def test_read_ir_early_exit(self):
        x, y = self.sd.read_ir(lines=IR_LINES + ["extra\n", "    4:   400.00      0.200000\n"])
        assert len(x) == 3, "should stop at blank line, not read extra"


class TestReadRamanIsolation:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/TD-DFT/UV_c60-Ih.out")

    def test_read_raman_lines(self):
        x, y = self.sd.read_raman(lines=RAMAN_LINES)
        assert len(x) == 3
        assert abs(x[0] - 100.0) < 1e-6
        assert abs(y[0] - 0.5) < 1e-6

    def test_read_raman_early_exit(self):
        x, y = self.sd.read_raman(lines=RAMAN_LINES + ["extra\n", "    4:   400.00      0.200000      0.500000\n"])
        assert len(x) == 3, "should stop at blank line, not read extra"


class TestReadVpt2Isolation:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/TD-DFT/UV_c60-Ih.out")

    def test_read_vpt2_lines(self):
        x, y = self.sd.read_vpt2(lines=VPT2_LINES)
        assert len(x) == 4
        # fundamental 1 → IR mode 7
        assert abs(x[0] - 490.0) < 1e-6
        assert abs(y[0] - 10.0) < 1e-6
        # fundamental 2 → IR mode 8
        assert abs(x[1] - 595.0) < 1e-6
        assert abs(y[1] - 20.0) < 1e-6
        # overtones
        assert abs(x[2] - 980.0) < 1e-6
        assert abs(y[2] - 5.0) < 1e-6
        assert abs(x[3] - 1190.0) < 1e-6
        assert abs(y[3] - 3.0) < 1e-6

    def test_read_vpt2_no_fundamentals(self):
        lines = ["no fundamental transitions here\n"]
        x, y = self.sd.read_vpt2(lines=lines)
        assert len(x) == 0

    def test_read_vpt2_no_ir_intensities(self):
        lines = [
            "Fundamental transitions\n",
            "---\n",
            "1  500.0  490.0  -10.0\n",
            "---\n",
            "no IR intensities here\n",
        ]
        x, y = self.sd.read_vpt2(lines=lines)
        assert len(x) == 0


ORCA5_ABS_LINES = [
    "Program Version 5.0.2\n",
    specstring_start + "\n",
    " 1   10000.0  0.500  0.100\n",
    " 2   20000.0  0.300  0.200\n",
    " 3   30000.0  0.100  0.050\n",
    specstring_end + "\n",
]

ORCA6_ABS_LINES = [
    "Program Version 6.0.0\n",
    specstring_start + "\n",
    " 1   10000.0  10000.0  10000.0  10000.0  0.500  0.100  0.050\n",
    " 2   20000.0  20000.0  20000.0  20000.0  0.300  0.200  0.100\n",
    " 3   30000.0  30000.0  30000.0  30000.0  0.100  0.050  0.025\n",
    specstring_end + "\n",
]


class TestReadOutAbsIsolation:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/TD-DFT/UV_c60-Ih.out")

    def test_orca5_column_indices(self):
        x, y = self.sd.read_out_abs(lines=ORCA5_ABS_LINES)
        assert len(x) == 3
        assert abs(x[0] - 10000.0) < 1e-6  # col 1 (0-indexed): energy
        assert abs(y[0] - 0.100) < 1e-6    # col 3: intensity

    def test_orca6_column_indices(self):
        x, y = self.sd.read_out_abs(lines=ORCA6_ABS_LINES)
        assert len(x) == 3
        assert abs(x[0] - 10000.0) < 1e-6  # col 4 (0-indexed): energy
        assert abs(y[0] - 0.050) < 1e-6    # col 7: intensity
