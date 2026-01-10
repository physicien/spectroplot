# `spectroplot`

Plot UV/Vis spectrum from ORCA output file and much more. (**TO UPDATE**)

<!-- ![show](examples/show-use3.gif) -->

A Python 3 script for (hassle-free) plotting of absorption spectra from output files with peak detection and annotation.
It combines the stick spectrum with the convoluted spectrum (lorentzian or gaussian line shape).
The script supports energy (wave number or electron-volt, cm<sup>-1</sup> or eV) and wavelength (λ, nm) plots.
The full spectrum or parts of the spectrum can be plotted. (**TO UPDATE**)

### Quick start

 Start the script with:

```console
python3 orca-uv.py [OPTION] filename
```

it will save the plot as SVG :
`spectrum.svg`

### Command-line options

- `filename` , required: filename (.out, .asc, .spectrum, .spectrum.rootX)
- `-s` , optional: shows the `matplotlib` window
- `-n` , optional: do not save the spectrum
- `-acs` , optional: format the plot to ACS publications standard format
- `-o` `str` , optional: change the name of the savec spectrum
- `-pnm` , optional: plot the wavelength (λ, nm) spectrum (default)
- `-pwn` , optional: plot the wave number (energy, cm<sup>-1</sup>) spectrum
- `-pev` , optional: plot the electron-volt (energy, eV) spectrum
- `-lsg` , optional: use the gaussian line shape function (default is lorentzian line shape)
- `-PL` , optional: use the PL Intensity y-axis label (default is Absorbance)
- `-wnm` `N` , optional: line width of the line shape for the nm scale (default is `N = 20`)
- `-wwn` `N` , optional: line width of the line shape for the cm<sup>-1</sup> scale (default is `N = 1000`)
- `-wev` `N` , optional: line width of the line shape for the eV scale (default is `N = 0.1`)
- `-x0`  `N` , optional: start spectrum at N nm or N cm<sup>-1</sup> (`x0 => 0`)
- `-x1`  `N` , optional: end spectrum at N nm or N cm<sup>-1</sup> (`x1 => 0`)
- `-y1`  `N` , optional: end statically spectrum at N a.u. (`y1 => 0`)
- `-swn` `N` , optional: shift the spectrum by N cm<sup>-1</sup> (default is `N = 0`)
- `-sev` `N` , optional: shift the spectrum by N eV (default is `N = 0`)

### Script options

There are numerous ways to configure the spectrum in the script:
Check `# plot config section - configure here` in the script. 
You can even configure the script to plot of the single line shape functions. (**TO UPDATE**)

### Code options

Colors, line thickness, line styles, level of peak detection and 
more can be changed in the code directly. (**TO UPDATE**)

### Remarks

The SVG file will be replaced everytime you start the script with the same output file. 
If you want to keep the file, you have to rename it. 
The data are taken from the section "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS". (**TO UPDATE**)

## Examples:

<!--
![Example 1](examples/example1.png)
![Example 2](examples/example2.png)
![Example 3](examples/example3.png)
-->

## Requirements
- `sys`

- `re`

- `argparse`

- `numpy`

- `pandas`
  
- `matplotlib`

- `seaborn`

- `scipy`

## Contributor

Contributed by Emmanuel Bourret

Based on `orca_uv` by [Sebastian Dechert](https://github.com/radi0sus/orca_uv)

## TO TO

- Change the line color/style when the same type of data type is plotted multiple times.

- Implement IR spectra (intensity and transmittance) as well as their VPT2 corrections.

- Implement Raman spectra?

- Update `README.md`

- Add examples
