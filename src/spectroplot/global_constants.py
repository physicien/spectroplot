#global constants
#plot config section - configure here
th_fac = 1.00                       #factor of the focs obtained from TD-DFT
esd_fac = 1.00                      #factor of the focs obtained from ESD
ex_fac = 1.00                       #factor of the focs obtained from Expt 
color_palette = "hls"               #color palette root/single line shape
label_tddft = "TD-DFT"              #label td-dft convolution plot
label_sticks = "VEE"                #label td-dft sticks plot
label_expt = "Expt."                #label experimental plot
label_roots = "ESD"                 #label root convolution plot
label_ir = "IR"                     #label ir spectrum plot
label_raman = "Raman"               #label raman spectrum plot
label_vpt2 = "VPT2"                 #label vpt2 spectrum plot
label_vpt2_overt = "Overt. + Comb." #label vpt2 overtones and combination bands
label_sticks_vib = "Calc. Trans."   #label ir/vpt2 stick spectra

show_single_lineshape = False       #show single line shape functions if True
show_single_lineshape_area = False  #show single line shape areas if True
show_conv_spectrum = True           #show the convoluted spectra if True 
show_sticks = True                  #show the stick spectra if True
show_exp_spectrum = True            #show the experimental spectra if True
show_single_root_area = True        #show single ESD root area plot if True 
show_esd_spectrum = True            #show the ESD spectra if True
show_label_peaks = True             #show peak labels if True
show_label_roots = True             #show root labels if True
show_minor_ticks = True             #show minor ticks if True
show_grid = False                   #show grid if True
show_legend = True                  #show the legend
linear_locator = None               #number of ticks (None = automatic, int = fixed count)
y_label = "Absorbance (arb. units)"      #label of the y-axis - ABS (default)
y_label_PL = "PL Intensity (arb. units)"#label of the y-axis - PL
y_label_ir = "IR Intensity (arb. units)"#label of the y-axis - IR
y_label_raman = "Raman Intensity (arb. units)"#label of the y-axis - Raman
x_label_wn = r'Wavenumber (cm$^{-1}$)'      #label of the x-axis - wave number
x_label_ev = r'Energy (eV)'             #label of the x-axis - eV
x_label_nm = r'Wavelength (nm)'         #label of the x-axis - nm
label_rotation_angle = 45                   #angle of the label
figure_dpi = 300                        #DPI of the picture
acs_w = 360                             #ACS format width - pt
acs_h = 180                             #ACS format height - pt
output_name = "spectrum"                #output file name


#CONSTANTS SECTION - go away if you don't know what you're doing
#start reading orca.out for VPT2 data from here
VPT2_STRING = 'ORCA VPT2/GVPT2 Analysis' #start reading orca.out for VPT2 data
#start reading orca.out for IR data from here
IR_STRING = 'IR SPECTRUM'                #start reading orca.out for IR data
#start reading orca.out for Raman data from here
RAMAN_STRING = 'RAMAN SPECTRUM'          #start reading orca.out for Raman data
#start reading orca.out for uv data from here
SPECSTRING_START = 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS'
#stop reading orca.out from here
SPECSTRING_END = 'ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS'
#pattern to match ESD root file extension (.spectrum.rootX)
RE_SPECTRUM_ROOT_PATTERN = r"\.spectrum\.root\d+$"
w_nm = 20       #w = line width for broadening - nm, FWHM
w_wn = 1000     #w = line width for broadening - wave numbers, FWHM
w_ev = 0.1      #w = line width for broadening - eV, FWHM
w_ir = 20        #w = line width for broadening - IR, FWHM (cm**-1)
w_raman = 20     #w = line width for broadening - Raman, FWHM (cm**-1)
npt_nm = 10     #npt = nb of pts per unit to calculate the line shape in nm
npt_wn = 1      #npt = nb of pts per unit to calculate the line shape in cm**-1
npt_ev = 1000   #npt = nb of pts per unit to calculate the line shape in eV
CONV_WNTOEV = 8065.54   #conversion factor from cm**-1 to eV

