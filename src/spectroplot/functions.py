from typing import Optional
import numpy as np                      #element-wise tensor processing
import pandas as pd                     #dataframe processing
from spectroplot.global_constants import npt_nm, npt_wn, npt_ev, CONV_WNTOEV
from spectroplot._patterns import RE_SPECTRUM_ROOT

def show_plots(ext: str, s: list[bool]) -> bool:
    #check if the file is needed for the plot asked by the user
    if ext == ".out":
        return s[0] or s[1] or s[2] or s[3]
    elif ext == ".asc":
        return s[4]
    elif ext == ".spectrum" or RE_SPECTRUM_ROOT.search(ext):
        return s[5] or s[6]
    return False

def is_unique(s: pd.Series) -> bool:
    #check if all values are identical
    #an empty series trivially has all identical elements
    a = s.to_numpy()
    if len(a) == 0:
        return True
    return bool((a[0] == a).all())

def rootSum(df: pd.DataFrame) -> pd.DataFrame:
    #check if all the roots come from the same system
    data = df[df["root_number"] > 0]
    if not is_unique(data["name"]):
        raise ValueError("Roots from different systems.")
    name = data["name"].iloc[0]
    #check if all the roots have the same xdata
    samex = [np.array_equal(data["xdata"].iloc[0], row["xdata"]) for i,row in data.iterrows()]
    if not all(samex):
        raise ValueError("Roots have different xdata.")
    else:
        xdata = data["xdata"].iloc[0]
    temp = np.array(data["ydata"].to_list())
    new_ydata = np.sum(temp,axis=0)
    output: dict = {
        "path": "None",
        "name": name,
        "ext": ".spectrum",
        "root_number": 0,
        "xdata": xdata,
        "ydata": new_ydata,
    }
    return pd.DataFrame([output])

def plotxrange(df: pd.DataFrame, x1: Optional[float], npt: int) -> np.ndarray:
    #return the x range for td-dft
    #plotrange must start at 0 for peak detection
    xmax_data = df["xdata_plot_max"].max()
    if x1 is not None and x1 > xmax_data:
        maxrange = x1
    else:
        maxrange = xmax_data
    return np.arange(0,maxrange,1/npt)

def roundup(x: float, ev_plot: bool, wn_plot: bool, nm_plot: bool) -> float:
    #round to next 1 or 10 or 100
    if ev_plot:
        return x if x % 1 == 0 else x + 1 - x % 1
    elif wn_plot:
        return x if x % 100 == 0 else x + 100 - x % 100
    elif nm_plot:
        return x if x % 10 == 0 else x + 10 - x % 10
    return x

def rounddown(x: float, ev_plot: bool, wn_plot: bool, nm_plot: bool) -> float:
    #round to previous 1 or 10 or 100
    if ev_plot:
        return x if x % 1 == 0 else x - x % 1
    elif wn_plot:
        return x if x % 100 == 0 else x - x % 100
    elif nm_plot:
        return x if x % 10 == 0 else x - x % 10
    return x

def lineshape(a: float, m: np.ndarray, x: float, w: float,
              ls_gauss: bool) -> np.ndarray:
    #calculation of the line shape
    # a = amplitude (max y, intensity)
    # m = full x-range array over which to compute the line shape
    # x = stick position (wave number or energy)
    # w = line width, FWHM
    if ls_gauss:
        #Gaussian line shape
        return a*np.exp(-(np.log(2)*(2*(m-x)/w)**2))
    else:
        #Lorentzian line shape (default)
        return a/(1+(2*(m-x)/w)**2)

def normalization(x: np.ndarray) -> np.ndarray:
    #normalize the spectrum between 0 and 1
    return (x-np.amin(x))/(np.amax(x)-np.amin(x))

def atLeastTwo(a: bool, b: bool, c: bool) -> bool:
    #return true if at least two elements out of three are true
    return a and (b or c) or (b and c)

def plotType(nm: bool, wn: bool, ev: bool) -> tuple[str, int]:
    #return the plot type and npt
    if nm:
        return "nm", npt_nm
    if wn:
        return "wn", npt_wn
    if ev:
        return "ev", npt_ev
    return "wn", npt_wn

def wntonm(wn: np.ndarray) -> np.ndarray:
    #cm**-1 to nm converter
    return 1e7 / np.asarray(wn)

def wntoev(wn: np.ndarray) -> np.ndarray:
    #cm**-1 to eV converter
    return np.asarray(wn) / CONV_WNTOEV

def nmtown(wl: np.ndarray) -> np.ndarray:
    #nm to cm**-1 converter
    return 1e7 / np.asarray(wl)

def nmtoev(wl: np.ndarray) -> np.ndarray:
    #nm to eV converter
    return 1e7 / np.asarray(wl) / CONV_WNTOEV

def unitConverter(data: np.ndarray, ext: str, unit: str) -> np.ndarray:
    #convert the x-axis data to the right units (nm, cm**-1, eV)
    if ext == ".asc":
        if unit == "wn":
            return nmtown(data)
        elif unit == "ev":
            return nmtoev(data)
        return np.asarray(data)
    if unit == "nm":
        return wntonm(data)
    elif unit == "ev":
        return wntoev(data)
    return np.asarray(data)

def xdataPrep(row: pd.Series, unit: str, shift: float) -> np.ndarray:
    #convert spectrum x-axis units and shift it if not experimental
    ext = row["ext"]
    if ext == ".asc":
        data = row["xdata"]
    else:
        data = np.asarray(row["xdata"]) + shift
    return unitConverter(data, ext, unit)

def xdatamin(row: pd.Series, w: float) -> float:
    #find the x-axis minimum
    ext = row["ext"]
    data = row["xdata_plot"]
    if ext == ".asc":
        return min(data)-w*3
    else:
        return min(data)

def xdatamax(row: pd.Series, w: float) -> float:
    #find the x-axis maximum
    ext = row["ext"]
    data = row["xdata_plot"]
    if ext == ".asc":
        return max(data)+w*3
    else:
        return max(data)

