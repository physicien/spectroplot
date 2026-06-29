import sys
sys.path.insert(0, "..")

from data_reader import SpectrumData


DATA_DIR = "data"


class TestSpectrumDataAsc:
    def setup_method(self):
        self.sd = SpectrumData(f"{DATA_DIR}/expt_data/C60.asc")

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

    def test_data_ranges(self):
        x, y = self.sd.data
        assert all(isinstance(v, float) for v in x)
        assert all(isinstance(v, float) for v in y)
        assert x[0] > x[-1]  # wavelengths descending


class TestSpectrumDataSpectrum:
    def setup_method(self):
        self.sd = SpectrumData(
            f"{DATA_DIR}/FLUOR/lw100/FLUOR_c60-Ih_esd.spectrum"
        )

    def test_filetype(self):
        assert self.sd.filetype == ".spectrum"

    def test_name(self):
        assert self.sd.name == "FLUOR_c60-Ih_esd"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

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
        self.sd = SpectrumData(f"{DATA_DIR}/td-dft/UV_c60-Ih.out")

    def test_filetype(self):
        assert self.sd.filetype == ".out"

    def test_name(self):
        assert self.sd.name == "UV_c60-Ih"

    def test_rootnumber(self):
        assert self.sd.rootnumber == 0

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

    def test_data_length(self):
        x, y = self.sd.data
        assert len(x) == len(y)
        assert len(x) > 0

    def test_first_values(self):
        x, y = self.sd.data
        assert abs(x[0] - 10002.83) < 1e-2
        assert abs(y[0] - 5.291294e-01) < 1e-6
