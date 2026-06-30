import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "src")

DATA_DIR = "data"

TEST_FILES = {
    "tddft": f"{DATA_DIR}/TD-DFT/UV_c60-Ih.out",
    "experimental": f"{DATA_DIR}/experimental/C60.asc",
    "esd": f"{DATA_DIR}/ESD/FLUOR/lw100/FLUOR_c60-Ih_esd.spectrum",
    "esd_root": f"{DATA_DIR}/ESD/ABS/ABS_pyrene_esd.spectrum.root1",
    "ir": f"{DATA_DIR}/IR/FRQ_tungsten_hexacarbonyl_f.out",
    "raman": f"{DATA_DIR}/Raman/RAM_c60-Ih_r.out",
    "vpt2": f"{DATA_DIR}/VPT2/VPT2_furan_vpt2.out",
    "nonexistent": "data/nonexistent.out",
}


class TestMainIntegration:
    @patch("spectroplot.spectroplot.plt.subplots")
    @patch("spectroplot.spectroplot.plt.savefig")
    @patch("spectroplot.spectroplot.plt.show")
    @patch("spectroplot.spectroplot.sns.color_palette")
    @patch("spectroplot.spectroplot.sns.set_palette")
    def _run_main(self, args, mock_set_palette, mock_color_palette,
                  mock_show, mock_savefig, mock_subplots):
        mock_ax = MagicMock()
        mock_fig = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        mock_ax.get_xlim.return_value = (0, 50000)
        mock_color_palette.return_value = ["red", "blue", "green"] * 10

        from spectroplot.spectroplot import main
        cli_args = ["spectroplot", *args, "-n"]
        with patch.object(sys, "argv", cli_args):
            main()
        return mock_ax

    def test_tddft(self):
        mock_ax = self._run_main([TEST_FILES["tddft"]])
        assert mock_ax.plot.called, "ax.plot should be called for TD-DFT"
        assert mock_ax.stem.called, "ax.stem should be called for TD-DFT"

    def test_experimental(self):
        mock_ax = self._run_main([TEST_FILES["experimental"]])
        assert mock_ax.plot.called, "ax.plot should be called for experimental"

    def test_esd(self):
        mock_ax = self._run_main([TEST_FILES["esd"]])
        assert mock_ax.plot.called, "ax.plot should be called for ESD"

    def test_esd_root(self):
        mock_ax = self._run_main([TEST_FILES["esd_root"]])
        assert mock_ax.fill_between.called, \
            "ax.fill_between should be called for ESD root"

    def test_ir(self):
        mock_ax = self._run_main([TEST_FILES["ir"]])
        assert mock_ax.plot.called, "ax.plot should be called for IR"
        assert mock_ax.stem.called, "ax.stem should be called for IR"

    def test_raman(self):
        mock_ax = self._run_main([TEST_FILES["raman"]])
        assert mock_ax.plot.called, "ax.plot should be called for Raman"
        assert mock_ax.stem.called, "ax.stem should be called for Raman"

    def test_vpt2(self):
        mock_ax = self._run_main([TEST_FILES["vpt2"]])
        assert mock_ax.plot.called, "ax.plot should be called for VPT2"
        assert mock_ax.stem.called, "ax.stem should be called for VPT2"

    def test_nonexistent_file_skipped(self):
        from spectroplot.spectroplot import main
        cli_args = ["spectroplot", TEST_FILES["nonexistent"], "-n"]
        with (
            patch.object(sys, "argv", cli_args),
            patch("spectroplot.spectroplot.plt.subplots"),
            patch("spectroplot.spectroplot.plt.savefig"),
            patch("spectroplot.spectroplot.plt.show"),
            patch("spectroplot.spectroplot.sns.color_palette"),
            patch("spectroplot.spectroplot.sns.set_palette"),
        ):
            with pytest.raises(SystemExit):
                main()

    def test_mixed_types(self):
        mock_ax = self._run_main([TEST_FILES["tddft"], TEST_FILES["experimental"]])
        assert mock_ax.plot.called

    def test_multiple_esd_roots(self):
        mock_ax = self._run_main([
            f"{DATA_DIR}/ESD/ABS/ABS_pyrene_esd.spectrum.root1",
            f"{DATA_DIR}/ESD/ABS/ABS_pyrene_esd.spectrum.root2",
        ])
        assert mock_ax.plot.called or mock_ax.fill_between.called

    def test_custom_output_png(self):
        mock_ax = self._run_main(
            [TEST_FILES["tddft"], "-o", "test_out.png"]
        )
        assert mock_ax.plot.called

    def test_show_flag(self):
        with (
            patch("spectroplot.spectroplot.plt.subplots") as mock_subplots,
            patch("spectroplot.spectroplot.plt.savefig"),
            patch("spectroplot.spectroplot.plt.show") as mock_show,
            patch("spectroplot.spectroplot.sns.color_palette"),
            patch("spectroplot.spectroplot.sns.set_palette"),
        ):
            mock_ax = MagicMock()
            mock_fig = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_ax.get_xlim.return_value = (0, 50000)

            from spectroplot.spectroplot import main
            cli_args = ["spectroplot", TEST_FILES["tddft"], "-s"]
            with patch.object(sys, "argv", cli_args):
                main()
            assert mock_show.called, "plt.show should be called with -s flag"

    def test_acs_format(self):
        mock_ax = self._run_main([TEST_FILES["tddft"], "-acs"])
        assert mock_ax.plot.called
        assert mock_ax.spines.__getitem__.called, \
            "ax.spines should be accessed in ACS format"


class TestDataReaderErrors:
    def test_nonexistent_file_raises(self):
        from spectroplot.data_reader import SpectrumData
        with patch("builtins.open") as mock_open:
            mock_open.side_effect = FileNotFoundError("no such file")
            try:
                SpectrumData("fake_path.out")
            except IOError:
                pass
            else:
                assert False, "Expected IOError for nonexistent file"

    def test_unknown_extension_raises(self):
        from spectroplot.data_reader import SpectrumData
        try:
            SpectrumData("data/TD-DFT/UV_c60-Ih.out.unknown")
        except ValueError as e:
            assert "Unknown file extension" in str(e)
        else:
            assert False, "Expected ValueError for unknown extension"
