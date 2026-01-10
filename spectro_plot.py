#!/usr/bin/python3
import sys                              #sys files processing
import re                               #regex
import argparse                         #argument parser
import numpy as np                      #element-wise tensor processing
import pandas as pd                     #dataframes processing
import matplotlib.pyplot as plt         #plots
import seaborn as sns                   #color palettes
from scipy.signal import find_peaks     #peak detection

from global_constants import *          #global_constants
from functions import *                 #functions
from data_reader import SpectrumData    #spectrum data parser

#global list
xdata_list = list()
ydata_list = list()
peaks_list = list()
roots_list = list()
ymax_list = list()

#create parser
parser = argparse.ArgumentParser(prog='spectro_plot',\
        description='Easily plor optical spectra from orca.out,\
        orca.spectrum,orca.spectrum.rootX, and expt.asc')

#filename is required
parser.add_argument("filename",
                    nargs='+',
                    help="the .out/.spectrum/.spectrum.rootX/.asc file"
                    )

#show the matplotlib window
parser.add_argument('-s','--show',
                    default=0,
                    action='store_true',
                    help='show the plot window'
                    )

#do not save svg file of the spectrum
parser.add_argument('-n','--nosave',
                    default=1,
                    action='store_false',
                    help='do not save the spectrum'
                    )

#format the spectrum following the ACS guidelines
parser.add_argument('-acs','--acs_format',
                    default=0,
                    action='store_true',
                    help='change the format of the plot to the \
                            ACS publication format'
                    )

#change the name of the output file
parser.add_argument('-o','--output_name',
                    type=str,
                    default=output_name,
                    help='change the name of the saved spectrum'
                    )

#plot the spectrum in nm
parser.add_argument('-pnm','--plotnm',
                    default=1,
                    action='store_true',
                    help='plot the spectrum in nm'
                    )

#plot the spectrum in cm**-1
parser.add_argument('-pwn','--plotwn',
                    default=0,
                    action='store_true',
                    help='plot the spectrum in cm**-1'
                    )

#plot the spectrum in eV
parser.add_argument('-pev','--plotev',
                    default=0,
                    action='store_true',
                    help='plot the spectrum in eV'
                    )

#change the line shape for a Gaussian line shape
parser.add_argument('-lsg','--lineshape_gauss',
                    default=0,
                    action='store_true',
                    help='use the gaussian line shape function'
                    )

#label y-axis - PL
parser.add_argument('-PL','--axisPL',
                    default=0,
                    action='store_true',
                    help='change the y-axis from ABS to PL'
                    )

#change the line width (interger) for line broadening - nm
parser.add_argument('-wnm','--linewidth_nm',
                    type=int,
                    default=w_nm,
                    help='line width for broadening - wavelength in nm'
                    )

#change the line width (integer) for line broadening - wn
parser.add_argument('-wwn','--linewidth_wn',
                    type=int,
                    default=w_wn,
                    help='line width for broadening - wave number in cm**-1'
                    )

#change the line width (float) for line broadening - eV
parser.add_argument('-wev','--linewidth_ev',
                    type=float,
                    default=w_ev,
                    help='line width for broadening = energy in eV'
                    )

#individial x range - start
parser.add_argument('-x0','--startx',
                    type=float,
                    help='start spectrum at x nm or cm**-1 or eV'
                    )

#individual x range - end
parser.add_argument('-x1','--endx',
                    type=float,
                    help='end spectrum at x nm or cm**-1 or eV'
                    )

#individual y range - end
parser.add_argument('-y1','--endy',
                    type=float,
                    help='maximum y of the spectrum'
                    )

#horizontal shift in cm**-1
parser.add_argument('-swn','--shiftwn',
                    type=float,
                    default=0.0,
                    help='shift the spectrum in cm**-1'
                    )

#horizontal shift in eV
parser.add_argument('-sev','--shiftev',
                    type=float,
                    default=0.0,
                    help='shift the spectrum in eV'
                    )

#parse the arguments
args = parser.parse_args()

#change values according to arguments
show_spectrum = args.show           #show the plot window if True
save_spectrum = args.nosave         #do not save the plot if True
filename = "{:s}.svg".format(args.output_name)  #saved plot name
acs_format = args.acs_format        #ACS Publications figure format
nm_plot = args.plotnm               #wavelength plot /nm if True (default)
if args.plotwn or args.plotev:
    nm_plot = not args.plotnm
wn_plot = args.plotwn               #wave number plot /cm**-1 if True
ev_plot = args.plotev               #energy plot /eV if True
ls_gauss = args.lineshape_gauss     #gaussian line shape if True
                                    #lorentzian line shape if False (default)
if args.axisPL:                     #change the y-axis label for PL Intensity
    y_label = y_label_PL
shift_wn = args.shiftwn             #shift the spectrum in cm**-1
shift_ev = args.shiftev*conv_wntoev #shift the spectrum in eV

#check if more than one plotXX are true - exit if true
#if false, set the plot type
if atLeastTwo(nm_plot,wn_plot,ev_plot):
    print("Warning. Multiple types of unit set to true for the x-axis. Exit.")
    sys.exit(1)
else:
    #return the type of plot (nm,wn,ev) and npt
    #npt = number of points per unit to calculate the line shape
    plot_type,npt = plotType(nm_plot,wn_plot,ev_plot)

#check if w for nm is between 1 and 500, else reset to 20
if 1 <= args.linewidth_nm <= 500:
    w_nm = args.linewidth_nm
else:
    print("warning! line width exceeds range, reset to 20")
    w_nm = 20

#check if w for wn is between 100 and 20000, else reset to 1000
if 100 <= args.linewidth_wn <= 20000:
    w_wn = args.linewidth_wn
else:
    print("warning! line width exceeds range, reset to 1000")
    w_wn = 1000

#check if w for eV is between 0.01 and 2.5, else reset to 0.1
if 0.01 <= args.linewidth_ev <= 2.5:
    w_ev = args.linewidth_ev
else:
    print("warning! line width exceeds range, reset to 0.1")
    w_ev = 0.1

#check if startx and endx are equal - exit if true
if args.startx is not None and args.endx is not None \
        and args.startx == args.endx:
    print("Warning. x0 and x1 are equal. Exit.")
    sys.exit(1)

#check if startx < 0 - exit if true
if args.startx:
    if args.startx < 0:
        print("Warning. x0 < 0. Exit.")
        sys.exit(1)

#check if endx < 0 - exit if true
if args.endx:
    if args.endx < 0:
        print("Warning. x1 < 0. Exit.")
        sys.exit(1)

#check if endy < 0 - exit if true
if args.endy:
    if args.endy < 0:
        print("Warning. y1 < 0. Exis.")
        sys.exit(1)

#check if shiftwn and shiftev are both defined - exit if true
if args.shiftwn != 0 and args.shiftev != 0:
    print("Warning. Both shifts in cm**-1 and in eV are defined. Exit.")
    sys.exit(1)
else:
    shift=shift_wn+shift_ev

#choose the right linewidth for the right plot type
if ev_plot:
    w = w_ev    #use linewidth in eV
elif wn_plot:
    w = w_wn    #use linewidth in cm**-1
else:
    w = w_nm    #use linewidth in nm

#parse input files
data_list = list()
spectra_list = list()
shows_list = [show_single_lineshape,show_single_lineshape_area,
              show_conv_spectrum,show_sticks,show_exp_spectrum,
              show_esd_spectrum,show_single_root_area]
for index,path in enumerate(args.filename):
    spectrum = SpectrumData(path)
    spectrum_data = {
            "path": spectrum.path,
            "name": spectrum.name,
            "ext": spectrum.filetype,
            "root_number": spectrum.rootnumber,
            "xdata": spectrum.data[0],
            "ydata": spectrum.data[1],
    }
    #keep the data only if this type of plot is requested
    if show_plots(spectrum.filetype,shows_list):
        continue
    #add the data to the dataset
    spectra_list.append(spectrum_data)
if not spectra_list:
    #check if spectra_list is empty - exit if true
    print("Warning. You are requesting an empty plot. Exit.")
    sys.exit(1)

#sort the dataset and convert it into a dataframe
data_list = sorted(spectra_list, key=lambda d: float(d["root_number"]))
df = pd.DataFrame(data_list)

#if possible, add the sum of all the ESD roots
if not df[df["root_number"] > 0].empty:
    df = pd.concat([df,rootSum(df)],ignore_index=True)

#data processing for the plots
df["xdata_plot"] = df.apply(xdataPrep,axis=1,unit=plot_type,shift=shift)
df["xdata_plot_min"] = df.apply(xdatamin,axis=1,w=w)
df["xdata_plot_max"] = df.apply(xdatamax,axis=1,w=w)

#set font size and plot parameters
if acs_format:
    width = acs_w/72            #width of the plot (in pt)
    height = acs_h/72           #height of the plot (in pt)
    s1,s2,s3,s4 = 5,6,7,7       #font sizes (in pt)
    lw = 0.75                   #line width (in pt)
    major_tick=4                #major tick length (in pt)
    minor_tick=2                #minor tick length (in pt)
else:
    width = 11.6                #width of the plot (in pt)
    height = 7.2                #height of the plot (in pt)
    s1,s2,s3,s4 = 14,16,18,8    #font sizes (in pt)
    lw = 0.80                   #line width (in pt)
    major_tick=8                #major tick length (in pt)
    minor_tick=4                #minor tick length (in pt)

plt.rcParams['figure.figsize'] = [width,height]
plt.rc('font', size=s2)
plt.rc('axes', titlesize=s3)
plt.rc('axes', labelsize=s3)
plt.rc('xtick', labelsize=s1)
plt.rc('ytick', labelsize=s1)
plt.rc('legend', fontsize=s1)

#prepare plot
palette = sns.color_palette("colorblind")
sns.set_palette(palette)
fig, ax = plt.subplots()

#plotrange must start at 0 for peak detection
plt_range_x = plotxrange(df,args.endx,npt)

#All the plots
for i, row in df.iterrows():
    #TD-DFT
    if row["ext"] == ".out":
        lineshape_sum = list()
        temp_lineshape_sum = list()
        xdata = row["xdata_plot"]
        ydata = row["ydata"]
        #normalization of the TD-DFT
        for index, wn in enumerate(xdata):
            temp_lineshape_sum.append(lineshape(ydata[index],plt_range_x,wn,w,
                                                ls_gauss))
            temp_range = np.sum(temp_lineshape_sum,axis=0)
            temp_min = min(temp_range)
            temp_max = max(temp_range)
            intenslist = (ydata-temp_min)/(temp_max-temp_min)*th_fac

        #color palette plot single lineshape function
        th_palette = sns.color_palette(color_palette, len(xdata))
        #plot single lineshape function for every frequency
        #generate summation of single lineshape functions
        for index, wn in enumerate(xdata):
            #single lineshape function line plot
            if show_single_lineshape:
                ax.plot(plt_range_x,
                        lineshape(intenslist[index],plt_range_x,wn,w,ls_gauss),
                        color=th_palette[index],alpha=0.5)
            #single lineshape function filled plot
            if show_single_lineshape_area:
                ax.fill_between(plt_range_x,
                                lineshape(intenslist[index],plt_range_x,wn,w,
                                          ls_gauss),
                                color=th_palette[index],alpha=0.5)
            #sum of lineshape functions
            if show_conv_spectrum:
                lineshape_sum.append(lineshape(intenslist[index],plt_range_x,wn,
                                               w,ls_gauss))

        #y values of the lineshape summation /cm**-1
        if show_conv_spectrum:
            plt_range_lineshape_sum_y = np.sum(lineshape_sum,axis=0)

        #plot the TD-DFT spectrum
        if show_conv_spectrum:
            #use the lineshape for peak detection
            xdata_list.append(plt_range_x)
            ydata_list.append(plt_range_lineshape_sum_y)
            ax.plot(plt_range_x,plt_range_lineshape_sum_y,color=palette[2],
                    linewidth=lw,label=label_tddft)

        if show_sticks:
            if not show_conv_spectrum:
                #use the sticks for peak detection
                xdata_list.append(xdata)
                ydata_list.append(intenslist)
            ax.stem(xdata,intenslist,linefmt="dimgrey",markerfmt=" ",
                    basefmt=" ",label=label_sticks)

    #EXPERIMENTAL
    if row["ext"] == ".asc":
        xdata = row["xdata_plot"]
        ydata = normalization(row["ydata"])*ex_fac
        xdata_list.append(xdata)
        ydata_list.append(ydata)
        if show_exp_spectrum:
            ax.plot(xdata,ydata,color=palette[0],linewidth=lw,
                    label=label_expt)

    #ESD
    if row["ext"] == ".spectrum":
        xdata = row["xdata_plot"]
        ydata = normalization(row["ydata"])*esd_fac
        xdata_list.append(xdata)
        ydata_list.append(ydata)
        if show_esd_spectrum:
            ax.plot(xdata,ydata,color=palette[1],linewidth=lw,
                    label=label_roots)
    #ESD roots
    if re.search(".spectrum.root\d+",row["ext"]):
        xdata = row["xdata_plot"]
        ydata = row["ydata"]
        index = row["root_number"]-1
        #normalization of the ESD roots
        temp_range = rootSum(df)["ydata"][0]
        temp_min = min(temp_range)
        temp_max = max(temp_range)
        intenslist = (ydata-temp_min)/(temp_max-temp_min)*esd_fac
        xdata_list.append(xdata)
        ydata_list.append(intenslist)

        #color palette plot single root
        esd_palette = sns.color_palette(color_palette,df["root_number"].max())
        #plot single lineshape function for every root
        #single root filled plot
        if show_single_root_area:
            ax.fill_between(xdata,intenslist,color=esd_palette[index],
                            alpha=0.5)

#legend
if show_legend:
    ax.legend()

#label x axis
if ev_plot:
    ax.set_xlabel(x_label_ev)
elif wn_plot:
    ax.set_xlabel(x_label_wn)
else:
    ax.set_xlabel(x_label_nm)

#label y axis
ax.set_ylabel(y_label)
ax.get_yaxis().set_ticks([])    #remove ticks from y axis
#plt.tight_layout()              #tight layout

#show minor ticks
if show_minor_ticks:
    ax.minorticks_on()

#if startx argument is given - x-axis range
if args.startx:
    xlim_autostart = args.startx
#if startx argument is not given or zero - x-axis range
else:
    if args.startx == 0:
        xlim_autostart = 0
    #startx from data
    else:
        xlim_autostart = rounddown(df["xdata_plot_min"].min(),ev_plot,wn_plot,
                                   nm_plot)

#if endx argument is giver - x-axis range
if args.endx:
    xlim_autoend = args.endx
#if endx argument is not given or zero - x-axis range
else:
    if args.endx == 0:
        xlim_autoend = 0
    # auto endx from data
    else:
        xlim_autoend = roundup(max(plt_range_x),ev_plot,wn_plot,nm_plot)

#x should not be below zero - x-axis range
if xlim_autostart < 0:
    plt.xlim(0,xlim_autoend)
else:
    plt.xlim(xlim_autostart,xlim_autoend)

#y-axis range - user-defined or dynamic y range
xmin=ax.get_xlim()[0]   #get recent xlim min
xmax=ax.get_xlim()[1]   #get recent xlim max
df['plt_range_x'] = xdata_list
df['plt_range_y'] = ydata_list
for index, row in df.iterrows():
    full_xrange = row['plt_range_x']
    full_yrange = row['plt_range_y']
    if xmin > xmax:
        i_x = [i for i,v in enumerate(full_xrange) \
                if v > xmax and v < xmin ]
    if xmax > xmin:
        i_x = [i for i,v in enumerate(full_xrange) \
                if v > xmin and v < xmax ]
    xrange = full_xrange[min(i_x):max(i_x)]
    yrange = full_yrange[min(i_x):max(i_x)]
    ymax_list.append(max(yrange))

    #peaks detection for labeling
    if show_label_peaks and not re.search(".spectrum.root\d+",row["ext"]):
        #peaks detection
        peaks , _ = find_peaks(yrange,prominence=0.01)
        for j, peak_j in enumerate(peaks):
            peaks_list.append([xrange[peak_j],yrange[peak_j]])

    #roots detection for labeling
    if show_label_roots and re.search(".spectrum.root\d+",row["ext"]):
        #root peaks detection
        peaks , _ = find_peaks(yrange,prominence=0.01)
        xp_root = [xrange[i] for i in peaks]
        yp_root = [yrange[i] for i in peaks]
        if xp_root:
            x_pos = np.average(xp_root)
            y_pos = np.average(yp_root)
            roots_list.append([row["root_number"],x_pos,y_pos])

if args.endy:
    #user-defined y range
    ylim_max = args.endy
else:
    #dynamic y range
    ylim_max = max(ymax_list)
ax.set_ylim(0,ylim_max*1.1)  #+10% for labels

#label peaks
if show_label_peaks:
    for i,v in enumerate(peaks_list):
        p_label = "{:.2f}".format(v[0])
        ax.annotate(p_label,
                    xy=(v[0],v[1]),
                    ha="center",
                    rotation=a_label,
                    size=s4,
                    xytext=(0,5),
                    textcoords='offset points',
                    color="dimgray",
                    )

#label roots
if show_label_roots and show_single_root_area:
    esd_palette = sns.color_palette(color_palette,df["root_number"].max())
    for i,v in enumerate(roots_list):
        r_label = "{:d}".format(v[0])
        ax.annotate(r_label,
                    xy=(v[1],v[2]),
                    ha="center",
                    size=s1,
                    xytext=(0,5),
                    textcoords='offset points',
                    color=esd_palette[v[0]-1],
                    )

#tick locations at the beginning and end of the spectrum x-axis, evenly spaced
if linear_locator:
    ax.xaxis.set_major_locator(plt.LinearLocator())

#tick parameters
ax.tick_params(which='major',length=major_tick)
ax.tick_params(which='minor',length=minor_tick)

#show grid
if show_grid:
    ax.grid(True,whick='major',axis='x',color='black',
            linestyle='dotted',linewidth=0.5)

#acs format
if acs_format:
#    ax.get_yaxis().set_visible(False)
#    ax.spines[['top','left','right']].set_visible(False)
    ax.spines[['top','right']].set_visible(False)

#tight layout
plt.tight_layout()              #tight layout

#save the plot
if save_spectrum:
    plt.savefig(filename, dpi=figure_dpi)

#show the plot
if show_spectrum:
    plt.show()
