"""Spectroplot — plot optical spectra from ORCA output files.

Exports
-------
SpectrumData
    Class for reading and parsing spectrum files.
main
    CLI entry point.
"""

from spectroplot.data_reader import SpectrumData


def main() -> None:
    """CLI entry point. Imports ``spectroplot.spectroplot.main`` lazily
    to avoid pulling in heavy dependencies on package import."""
    from spectroplot.spectroplot import main as _main
    _main()
