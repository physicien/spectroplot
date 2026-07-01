import sys                              #sys files processing
from typing import Optional
from pathlib import Path                #path processing
import argparse                         #argument parser
import numpy as np                      #element-wise tensor processing
import pandas as pd                     #dataframes processing
import matplotlib.pyplot as plt         #plots
import seaborn as sns                   #color palettes
from scipy.signal import find_peaks     #peak detection

from spectroplot.global_constants import (
    th_fac, esd_fac, ex_fac, color_palette,
    label_tddft, label_sticks, label_expt, label_roots,
    label_ir, label_raman, label_vpt2, label_vpt2_overt,
    label_sticks_vib,
    show_single_lineshape, show_single_lineshape_area,
    show_conv_spectrum, show_sticks, show_exp_spectrum,
    show_esd_spectrum, show_single_root_area,
    show_label_peaks, show_label_roots,
    show_minor_ticks, show_grid, show_legend, linear_locator,
    y_label, y_label_PL, y_label_ir, y_label_raman,
    x_label_wn, x_label_ev, x_label_nm,
    a_label, figure_dpi, acs_w, acs_h, output_name,
    conv_wntoev, w_nm, w_wn, w_ev, w_ir, w_raman,
)
from spectroplot._patterns import RE_SPECTRUM_ROOT
from spectroplot.functions import (
    atLeastTwo, plotType, show_plots, rootSum,
    xdataPrep, xdatamin, xdatamax, plotxrange,
    lineshape, normalization, rounddown, roundup,
)
from spectroplot.data_reader import SpectrumData    #spectrum data parser


def _plot_tddft(ax, row, i, plt_range_x, w, ls_gauss, palette, lw,
                plot_data):
    lineshape_sum = []
    temp_lineshape_sum = []
    xdata = row["xdata_plot"]
    ydata = np.asarray(row["ydata"], dtype=float)

    for index, wn in enumerate(xdata):
        temp_lineshape_sum.append(lineshape(ydata[index], plt_range_x, wn, w,
                                            ls_gauss))
    temp_range = np.sum(temp_lineshape_sum, axis=0)
    temp_min = min(temp_range)
    temp_max = max(temp_range)
    intenslist = (ydata - temp_min) / (temp_max - temp_min) * th_fac

    th_palette = sns.color_palette(color_palette, len(xdata))
    for index, wn in enumerate(xdata):
        if show_single_lineshape:
            ax.plot(plt_range_x,
                    lineshape(intenslist[index], plt_range_x, wn, w, ls_gauss),
                    color=th_palette[index], alpha=0.5)
        if show_single_lineshape_area:
            ax.fill_between(plt_range_x,
                            lineshape(intenslist[index], plt_range_x, wn, w,
                                      ls_gauss),
                            color=th_palette[index], alpha=0.5)
        if show_conv_spectrum:
            lineshape_sum.append(lineshape(intenslist[index], plt_range_x, wn,
                                           w, ls_gauss))

    if show_conv_spectrum:
        plt_range_lineshape_sum_y = np.sum(lineshape_sum, axis=0)
        plot_data[i] = (plt_range_x, plt_range_lineshape_sum_y)
        ax.plot(plt_range_x, plt_range_lineshape_sum_y, color=palette[2],
                linewidth=lw, label=label_tddft)

    if show_sticks:
        if not show_conv_spectrum:
            plot_data[i] = (xdata, intenslist)
        ax.stem(xdata, intenslist, linefmt="dimgrey", markerfmt=" ",
                basefmt=" ", label=label_sticks)


def _plot_experimental(ax, row, i, palette, lw, plot_data):
    xdata = row["xdata_plot"]
    ydata = normalization(np.asarray(row["ydata"], dtype=float)) * ex_fac
    plot_data[i] = (xdata, ydata)
    if show_exp_spectrum:
        ax.plot(xdata, ydata, color=palette[0], linewidth=lw,
                label=label_expt)


def _plot_esd(ax, row, i, palette, lw, plot_data):
    xdata = row["xdata_plot"]
    ydata = normalization(np.asarray(row["ydata"], dtype=float)) * esd_fac
    plot_data[i] = (xdata, ydata)
    if show_esd_spectrum:
        ax.plot(xdata, ydata, color=palette[1], linewidth=lw,
                label=label_roots)


def _plot_esd_root(ax, row, i, root_sum, lw, df, plot_data):
    xdata = row["xdata_plot"]
    ydata = np.asarray(row["ydata"], dtype=float)
    index = row["root_number"] - 1
    temp_range = root_sum["ydata"][0]
    temp_min = min(temp_range)
    temp_max = max(temp_range)
    intenslist = (ydata - temp_min) / (temp_max - temp_min) * esd_fac
    plot_data[i] = (xdata, intenslist)

    esd_palette = sns.color_palette(color_palette,
                                    df["root_number"].max())
    if show_single_root_area:
        ax.fill_between(xdata, intenslist, color=esd_palette[index],
                        alpha=0.5)


def _plot_vib(ax, row, i, plt_range_x, w, ls_gauss, palette, lw,
              label, color_idx, plot_data):
    lineshape_sum = []
    xdata = row["xdata_plot"]
    ydata = row["ydata"]

    for index, wn in enumerate(xdata):
        if show_conv_spectrum:
            lineshape_sum.append(lineshape(ydata[index], plt_range_x, wn, w,
                                           ls_gauss))

    if show_conv_spectrum:
        plt_range_lineshape_sum_y = np.sum(lineshape_sum, axis=0)
        plot_data[i] = (plt_range_x, plt_range_lineshape_sum_y)
        ax.plot(plt_range_x, plt_range_lineshape_sum_y,
                color=palette[color_idx], linewidth=lw, label=label)

    if show_sticks:
        if not show_conv_spectrum:
            plot_data[i] = (xdata, ydata)
        ax.stem(xdata, ydata, linefmt="dimgrey", markerfmt=" ",
                basefmt=" ", label=label_sticks_vib)


def _plot_ir(ax, row, i, plt_range_x, w, ls_gauss, palette, lw, plot_data):
    _plot_vib(ax, row, i, plt_range_x, w, ls_gauss, palette, lw,
              label_ir, 3, plot_data)


def _plot_raman(ax, row, i, plt_range_x, w, ls_gauss, palette, lw,
                plot_data):
    _plot_vib(ax, row, i, plt_range_x, w, ls_gauss, palette, lw,
              label_raman, 5, plot_data)


def _plot_vpt2(ax, row, i, plt_range_x, w, ls_gauss, palette, lw,
               plot_data):
    lineshape_sum = []
    xdata = row["xdata_plot"]
    ydata = row["ydata"]
    nfund = row.get("vpt2_nfund", 0)
    fund_x = xdata[:nfund]
    fund_y = ydata[:nfund]
    overt_x = xdata[nfund:]
    overt_y = ydata[nfund:]

    for index, wn in enumerate(xdata):
        if show_conv_spectrum:
            lineshape_sum.append(lineshape(ydata[index], plt_range_x, wn, w,
                                           ls_gauss))

    if show_conv_spectrum:
        plt_range_lineshape_sum_y = np.sum(lineshape_sum, axis=0)
        plot_data[i] = (plt_range_x, plt_range_lineshape_sum_y)
        ax.plot(plt_range_x, plt_range_lineshape_sum_y, color=palette[4],
                linewidth=lw, label=label_vpt2)

    if show_sticks:
        if not show_conv_spectrum:
            plot_data[i] = (xdata, ydata)
        if nfund:
            ax.stem(fund_x, fund_y, linefmt="dimgrey", markerfmt=" ",
                    basefmt=" ", label=label_sticks_vib)
            ax.stem(overt_x, overt_y, linefmt=palette[4], markerfmt=" ",
                    basefmt=" ", label=label_vpt2_overt)
        else:
            ax.stem(xdata, ydata, linefmt="dimgrey", markerfmt=" ",
                    basefmt=" ", label=label_vpt2)


def main():
    #create parser
    parser = argparse.ArgumentParser(prog='spectroplot',\
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
                         help='output filename (.svg default, supports .png/.pdf)'
                        )

    #plot the spectrum in nm
    parser.add_argument('-pnm','--plotnm',
                        default=0,
                        action='store_true',
                        help='plot the spectrum in nm'
                        )

    #plot the spectrum in cm**-1
    parser.add_argument('-pwn','--plotwn',
                        default=1,
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
                        default=None,
                        help='shift the spectrum in cm**-1'
                        )

    #horizontal shift in eV
    parser.add_argument('-sev','--shiftev',
                        type=float,
                        default=None,
                        help='shift the spectrum in eV'
                        )

    #parse the arguments
    args = parser.parse_args()

    #change values according to arguments
    show_spectrum = args.show           #show the plot window if True
    save_spectrum = args.nosave         #do not save the plot if True
    #append .svg by default if no extension given
    filename = args.output_name if Path(args.output_name).suffix \
               else f"{args.output_name}.svg"
    acs_format = args.acs_format        #ACS Publications figure format
    nm_plot = args.plotnm               #wavelength plot /nm if True
    wn_plot = args.plotwn               #wave number plot /cm**-1 if True (default)
    ev_plot = args.plotev               #energy plot /eV if True
    ls_gauss = args.lineshape_gauss     #gaussian line shape if True
                                        #lorentzian line shape if False (default)
    ir_input = False
    raman_input = False
    vpt2_input = False
    shift_wn = args.shiftwn if args.shiftwn is not None else 0.0
    shift_ev = (args.shiftev if args.shiftev is not None else 0.0) * conv_wntoev

    #check if more than one plotXX are true - exit if true
    #if false, set the plot type
    if atLeastTwo(nm_plot,wn_plot,ev_plot):
        print("Warning. Multiple types of unit set to true for the x-axis. Exit.", file=sys.stderr)
        sys.exit(1)
    else:
        #return the type of plot (nm,wn,ev) and npt
        #npt = number of points per unit to calculate the line shape
        plot_type,npt = plotType(nm_plot,wn_plot,ev_plot)

    #check if w for nm is between 1 and 500, else reset to 20
    if 1 <= args.linewidth_nm <= 500:
        w_nm_use = args.linewidth_nm
    else:
        print("warning! line width exceeds range, reset to 20", file=sys.stderr)
        w_nm_use = 20

    #check if w for wn is between 100 and 20000, else reset to 1000
    if 100 <= args.linewidth_wn <= 20000:
        w_wn_use = args.linewidth_wn
    else:
        print("warning! line width exceeds range, reset to 1000", file=sys.stderr)
        w_wn_use = 1000

    #check if w for eV is between 0.01 and 2.5, else reset to 0.1
    if 0.01 <= args.linewidth_ev <= 2.5:
        w_ev_use = args.linewidth_ev
    else:
        print("warning! line width exceeds range, reset to 0.1", file=sys.stderr)
        w_ev_use = 0.1

    #check if startx and endx are equal - exit if true
    if args.startx is not None and args.endx is not None \
            and args.startx == args.endx:
        print("Warning. x0 and x1 are equal. Exit.", file=sys.stderr)
        sys.exit(1)

    #check if startx < 0 - exit if true
    if args.startx is not None and args.startx < 0:
        print("Warning. x0 < 0. Exit.", file=sys.stderr)
        sys.exit(1)

    #check if endx < 0 - exit if true
    if args.endx is not None and args.endx < 0:
        print("Warning. x1 < 0. Exit.", file=sys.stderr)
        sys.exit(1)

    #check if endy < 0 - exit if true
    if args.endy is not None and args.endy < 0:
        print("Warning. y1 < 0. Exit.", file=sys.stderr)
        sys.exit(1)

    #check if shiftwn and shiftev are both defined - exit if true
    if args.shiftwn is not None and args.shiftev is not None:
        print("Warning. Both shifts in cm**-1 and in eV are defined. Exit.", file=sys.stderr)
        sys.exit(1)
    else:
        shift=shift_wn+shift_ev

    #choose the right linewidth for the right plot type
    if ev_plot:
        w = w_ev_use    #use linewidth in eV
    elif wn_plot:
        w = w_wn_use    #use linewidth in cm**-1
    else:
        w = w_nm_use    #use linewidth in nm

    #parse input files
    spectra_list = list()
    shows_list = [show_single_lineshape,show_single_lineshape_area,
                  show_conv_spectrum,show_sticks,show_exp_spectrum,
                  show_esd_spectrum,show_single_root_area]
    for index,path in enumerate(args.filename):
        try:
            spectrum = SpectrumData(path)
        except (ValueError, IOError) as e:
            print(f"Warning: {e}", file=sys.stderr)
            continue
        if spectrum.spectrum_type == "ir":
            ir_input = True
        if spectrum.spectrum_type == "raman":
            raman_input = True
        if spectrum.spectrum_type == "vpt2":
            vpt2_input = True
        spectrum_data = {
                "path": spectrum.path,
                "name": spectrum.name,
                "ext": spectrum.filetype,
                "root_number": spectrum.rootnumber,
                "spectrum_type": spectrum.spectrum_type,
                "vpt2_nfund": spectrum.vpt2_nfund,
                "xdata": spectrum.data[0],
                "ydata": spectrum.data[1],
        }
        #skip data if this type of plot is not requested
        if show_plots(spectrum.filetype,shows_list):
            continue
        #add the data to the dataset
        spectra_list.append(spectrum_data)
    if not spectra_list:
        #check if spectra_list is empty - exit if true
        print("Warning. You are requesting an empty plot. Exit.", file=sys.stderr)
        sys.exit(1)

    #select y-axis label and linewidth based on input type
    y_label_use = y_label    # default from global_constants

    #sort the dataset and convert it into a dataframe
    data_list = sorted(spectra_list, key=lambda d: float(d["root_number"]))
    df = pd.DataFrame(data_list)

    #if possible, add the sum of all the ESD roots
    root_sum = None
    if not df[df["root_number"] > 0].empty:
        try:
            root_sum = rootSum(df)
        except ValueError as e:
            print(f"Warning: {e}", file=sys.stderr)
            root_sum = None
        if root_sum is not None:
            df = pd.concat([df, root_sum], ignore_index=True)

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
    plot_data: dict[int, tuple[Optional[np.ndarray], Optional[np.ndarray]]] = {}
    types_plotted: set[str] = set()
    for i, row in df.iterrows():
        if row["ext"] == ".out" and row["spectrum_type"] == "ir":
            types_plotted.add("IR")
            _plot_ir(ax, row, i, plt_range_x, w_ir, ls_gauss, palette, lw,
                     plot_data)
        elif row["ext"] == ".out" and row["spectrum_type"] == "raman":
            types_plotted.add("Raman")
            _plot_raman(ax, row, i, plt_range_x, w_raman, ls_gauss, palette,
                        lw, plot_data)
        elif row["ext"] == ".out" and row["spectrum_type"] == "vpt2":
            types_plotted.add("IR")
            _plot_vpt2(ax, row, i, plt_range_x, w_ir, ls_gauss, palette, lw,
                       plot_data)
        elif row["ext"] == ".out":
            _plot_tddft(ax, row, i, plt_range_x, w, ls_gauss, palette, lw,
                        plot_data)
        elif row["ext"] == ".asc":
            _plot_experimental(ax, row, i, palette, lw, plot_data)
        elif row["ext"] == ".spectrum":
            _plot_esd(ax, row, i, palette, lw, plot_data)
        elif RE_SPECTRUM_ROOT.search(row["ext"]):
            _plot_esd_root(ax, row, i, root_sum, lw, df, plot_data)

    if types_plotted:
        y_label_use = " / ".join(sorted(types_plotted)) + " Intensity (arb. units)"
    if args.axisPL:
        y_label_use = y_label_PL

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
    ax.set_ylabel(y_label_use)
    ax.get_yaxis().set_ticks([])    #remove ticks from y axis

    #show minor ticks
    if show_minor_ticks:
        ax.minorticks_on()

    #if startx argument is given - x-axis range
    if args.startx is not None:
        xlim_autostart = args.startx
    #startx from data
    else:
        xlim_autostart = rounddown(df["xdata_plot_min"].min(),ev_plot,wn_plot,
                                   nm_plot)

    #if endx argument is given - x-axis range
    if args.endx is not None:
        xlim_autoend = args.endx
    # auto endx from data
    else:
        xlim_autoend = roundup(max(plt_range_x),ev_plot,wn_plot,nm_plot)

    #x should not be below zero - x-axis range
    if xlim_autostart < 0:
        plt.xlim(0,xlim_autoend)
    else:
        plt.xlim(xlim_autostart,xlim_autoend)

    #y-axis range - user-defined or dynamic y range
    peaks_list: list[list[float]] = []
    roots_list: list[list[float]] = []
    ymax_list: list[float] = []
    xmin=ax.get_xlim()[0]   #get recent xlim min
    xmax=ax.get_xlim()[1]   #get recent xlim max
    df['plt_range_x'] = df.index.map(lambda i: plot_data.get(i, (None, None))[0])
    df['plt_range_y'] = df.index.map(lambda i: plot_data.get(i, (None, None))[1])
    for index, row in df.iterrows():
        full_xrange = row['plt_range_x']
        full_yrange = row['plt_range_y']
        if full_xrange is None:
            continue
        lo, hi = min(xmin, xmax), max(xmin, xmax)
        i_x = [i for i, v in enumerate(full_xrange) if lo < v < hi]
        if not i_x:
            continue
        xrange = full_xrange[min(i_x):max(i_x)]
        yrange = full_yrange[min(i_x):max(i_x)]
        ymax_list.append(max(yrange))

        #peaks detection for labeling
        if show_label_peaks and not RE_SPECTRUM_ROOT.search(row["ext"]):
            #peaks detection: skip peaks too close (<1% of x-range) or too weak
            x_range_span = xrange[-1] - xrange[0]
            dist_samples = max(1, int(x_range_span * npt * 0.01))
            peaks, _ = find_peaks(yrange, prominence=0.01,
                                  distance=dist_samples)
            y_max = max(yrange) if len(yrange) else 1
            for j, peak_j in enumerate(peaks):
                if yrange[peak_j] > 0.02 * y_max:
                    peaks_list.append([xrange[peak_j],yrange[peak_j]])

        #roots detection for labeling
        if show_label_roots and RE_SPECTRUM_ROOT.search(row["ext"]):
            #root peaks detection
            peaks , _ = find_peaks(yrange,prominence=0.01)
            xp_root = [xrange[i] for i in peaks]
            yp_root = [yrange[i] for i in peaks]
            if xp_root:
                x_pos = np.average(xp_root)
                y_pos = np.average(yp_root)
                roots_list.append([row["root_number"],x_pos,y_pos])

    if args.endy is not None:
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
    if show_label_roots and show_single_root_area and df["root_number"].max() > 0:
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
        ax.grid(True,which='major',axis='x',color='black',
                linestyle='dotted',linewidth=0.5)

    #acs format
    if acs_format:
        ax.spines[['top','right']].set_visible(False)

    #tight layout
    plt.tight_layout()              #tight layout

    #save the plot
    if save_spectrum:
        plt.savefig(filename, dpi=figure_dpi)

    #show the plot
    if show_spectrum:
        plt.show()
if __name__ == '__main__':
    main()
