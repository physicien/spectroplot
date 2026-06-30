import sys
sys.path.insert(0, "src")

from spectroplot.data_reader import SpectrumData


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
