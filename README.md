# `spectroplot`

Plot absorption and fluorescence spectra from ORCA output files, experimental data, and much more.

A Python 3 package for plotting optical spectra with peak detection and annotation.
It combines the stick spectrum with the convoluted spectrum (lorentzian or gaussian line shape).
The package supports energy (wave number or electron-volt, cm<sup>-1</sup> or eV) and wavelength (λ, nm) plots.
The full spectrum or parts of the spectrum can be plotted.

Supported data types:
- **TD-DFT** (`.out`): absorption and fluorescence from ORCA time-dependent density functional theory calculations
- **ESD** (`.spectrum`): absorption and fluorescence from ORCA excited state dynamics module
- **ESD roots** (`.spectrum.rootX`): individual root contributions from ESD
- **Experimental** (`.asc`): experimental spectra loaded as wavelength/intensity pairs

### Install

```console
pip install .
```

### Quick start

```console
spectroplot [OPTION] filename
```

or

```console
python3 -m spectroplot [OPTION] filename
```

It will save the plot as SVG: `spectrum.svg`

### Examples

```console
# TD-DFT absorption in nm
spectroplot data/TD-DFT/UV_c60-Ih.out -s -n
```

![TD-DFT absorption](examples/td-dft_abs.png)

```console
# TD-DFT + experimental overlaid
spectroplot data/TD-DFT/UV_c60-Ih.out data/experimental/C60.asc -s -n
```

![TD-DFT + experimental](examples/td-dft_expt.png)

```console
# ESD fluorescence in nm with Gaussian lineshape
spectroplot data/ESD/FLUOR/lw100/FLUOR_c60-Ih_esd.spectrum -s -n --lineshape_gauss
```

![ESD fluorescence](examples/esd_fluor.png)

```console
# ESD absorption in eV (all roots, 3-8 eV range)
spectroplot data/ESD/ABS/ABS_pyrene_esd.spectrum.root* -s -n --plotev -x0 3 -x1 8
```

![ESD absorption roots](examples/esd_abs_roots.png)

```console
# PL spectrum
spectroplot data/experimental/C60_PL.asc -s -n -PL
```

![PL spectrum](examples/expt_pl.png)

```console
# Custom output as PNG
spectroplot data/TD-DFT/UV_c60-Ih.out -o spectrum.png
```

![Custom PNG output](examples/custom_output.png)

### Command-line options

- `filename` , required: filename (.out, .asc, .spectrum, .spectrum.rootX)
- `-s` , optional: shows the `matplotlib` window
- `-n` , optional: do not save the spectrum
- `-acs` , optional: format the plot to ACS publications standard format
- `-o` `str` , optional: output filename (`.svg` default, supports `.png`/`.pdf`)
- `-pnm` , optional: plot the wavelength (λ, nm) spectrum
- `-pwn` , optional: plot the wave number (energy, cm<sup>-1</sup>) spectrum (default)
- `-pev` , optional: plot the electron-volt (energy, eV) spectrum
- `-lsg` , optional: use the gaussian line shape function (default is lorentzian line shape)
- `-PL` , optional: use the PL Intensity y-axis label (default is Absorbance)
- `-wnm` `N` , optional: line width of the line shape for the nm scale (default is `N = 20`)
- `-wwn` `N` , optional: line width of the line shape for the cm<sup>-1</sup> scale (default is `N = 1000`)
- `-wev` `N` , optional: line width of the line shape for the eV scale (default is `N = 0.1`)
- `-x0`  `N` , optional: start spectrum at N nm or N cm<sup>-1</sup> (`x0 => 0`)
- `-x1`  `N` , optional: end spectrum at N nm or N cm<sup>-1</sup> (`x1 => 0`)
- `-y1`  `N` , optional: end statically spectrum at N arb. units (`y1 => 0`)
- `-swn` `N` , optional: shift the spectrum by N cm<sup>-1</sup> (default is `N = 0`)
- `-sev` `N` , optional: shift the spectrum by N eV (default is `N = 0`)

### Script options

There are numerous ways to configure the spectrum.
Check `# plot config section - configure here` in `src/spectroplot/global_constants.py`.
You can even configure the script to plot of the single line shape functions.

### Remarks

The SVG file will be replaced every time you run the script with the same output name. 
For TD-DFT data, the absorption spectrum is taken from the section 
"ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in the ORCA output.

## Requirements

- `numpy`
- `pandas`
- `matplotlib`
- `seaborn`
- `scipy`

## Contributor

Contributed by Emmanuel Bourret

Based on `orca_uv` by [Sebastian Dechert](https://github.com/radi0sus/orca_uv)

## TO DO

- Change the line color/style when the same type of data type is plotted multiple times.

- Implement IR spectra (intensity and transmittance) as well as their VPT2 corrections.

- Implement Raman spectra?
