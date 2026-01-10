#!/usr/bin/python3
import sys                              #sys files processing
import re                               #regex
import numpy as np                      #element-wise tensor processing
import pandas as pd                     #dataframe processing
from global_constants import npt_nm, npt_wn, npt_ev, conv_wntoev

def show_plots(ext,s):
    #check if the file is needed for the plot asked by the user
    if ext == ".out" and not (s[0] or s[1] or s[2] or s[3]):
        return True
    elif ext == ".asc" and not s[4]:
        return True
    elif (ext == ".spectrum" or re.search(".spectrum.root\d+",ext)) and \
            not (s[5] or s[6]):
        return True

def is_unique(s):
    #check if all strings are the same 
    a = s.to_numpy()
    return (a[0] == a).all()

def rootSum(df):
    #check if all the roots come from the same system - exit if true
    data = df[df["root_number"] > 0]
    if not is_unique(data["name"]):
        print("Warning. Roots from different systems. Exit.")
        sys.exit(1)
    else:
        name = data["name"].iloc[0]
    #check if all the roots have the same xdata - exit if true
    samex = [data["xdata"].iloc[0] == row["xdata"] for i,row in data.iterrows()]
    if not all(samex):
        print("Warning. Roots have different xdata. Exit.")
        sys.exit(1)
    else:
        xdata = data["xdata"].iloc[0]
    temp = np.array(data["ydata"].to_list())
    new_ydata = np.sum(temp,axis=0)
    output = {
        "path": "None",
        "name": name,
        "ext": ".spectrum",
        "root_number": 0,
        "xdata": xdata,
        "ydata": new_ydata,
    }
    return pd.DataFrame([output])

def plotxrange(df,x1,npt):
    #return the x range for td-dft
    #plotrange must start at 0 for peak detection
    xmax_data = df["xdata_plot_max"].max()
    if x1 and x1 > xmax_data:
        maxrange = x1
    else:
        maxrange = xmax_data
    return np.arange(0,maxrange,1/npt)

def roundup(x,ev_plot,wn_plot,nm_plot):
    #round to next 1 or 10 or 100
    if ev_plot:
        return x if x % 1 == 0 else x + 1 - x % 1
    elif wn_plot:
        return x if x % 100 == 0 else x + 100 - x % 100
    elif nm_plot:
        return x if x % 10 == 0 else x + 10 - x % 10

def rounddown(x,ev_plot,wn_plot,nm_plot):
    #round to previous 1 or 10 or 100
    if ev_plot:
        return x if x % 1 == 0 else x - 1 - x % 1
    elif wn_plot:
        return x if x % 100 == 0 else x - 100 - x % 100
    elif nm_plot:
        return x if x % 10 == 0 else x - 10 - x % 10

def lineshape(a,m,x,w,ls_gauss):
    #calculation of the line shape
    # a = amplitude (max y, intensity)
    # x = position
    # m = maximum/meadian (stick position in x, wave number)
    # w = line width, FWHM
    if ls_gauss:
        #Gaussian line shape
        return a*np.exp(-(np.log(2)*(2*(m-x)/w)**2))
    else:
        #Lorentzian line shape (default)
        return a/(1+(2*(m-x)/w)**2)

def normalization(x):
    #normalize the spectrum between 0 and 1
    return (x-np.amin(x))/(np.amax(x)-np.amin(x))

def atLeastTwo(a,b,c):
    #return true if at least two elements out of three are true
    return a and (b or c) or (b and c);

def plotType(nm,wn,ev):
    #return the plot type and npt
    if nm:
        return "nm", npt_nm
    if wn:
        return "wn", npt_wn
    if ev:
        return "ev", npt_ev

def wntonm(wn):
    #cm**-1 to nm converter
    return [1/w*10**7 for w in wn]

def wntoev(wn):
    #cm**-1 to eV converter
    return [w/conv_wntoev for w in wn]

def nmtown(wl):
    #nm to cm**-1 converter
    return [1/w*10**7 for w in wl]

def nmtoev(wl):
    #nm to eV converter
    return [1/w*10**7/conv_wntoev for w in wl]

def unitConverter(data,ext,unit):
    #convert the x-axis data to the right units (nm, cm**-1, eV)
    if ext == ".asc":
        if unit == "wn":
            return nmtown(data)
        elif unit == "ev":
            return nmtoev(data)
        else:
            return data
    else:
        if unit == "nm":
            return wntonm(data)
        elif unit == "ev":
            return wntoev(data)
        else:
            return data

def xdataPrep(df,unit,shift):
    #convert spectrum x-axis units and shift it if not experimental
    ext = df["ext"]
    if ext == ".asc":
        data = df["xdata"]
    else:
        data = [x + shift for x in df["xdata"]]
    return unitConverter(data,ext,unit)

def xdatamin(df,w):
    #find the x-axis minimum
    ext = df["ext"]
    data = df["xdata_plot"]
    if ext == ".asc":
        return min(data)-w*3
    else:
        return min(data)

def xdatamax(df,w):
    #find the x-axis maximum
    ext = df["ext"]
    data = df["xdata_plot"]
    if ext == ".asc":
        return max(data)+w*3
    else:
        return max(data)

