from typing import Optional
import numpy as np                      #element-wise tensor processing
import pandas as pd                     #dataframe processing
from spectroplot.global_constants import npt_nm, npt_wn, npt_ev, CONV_WNTOEV
from spectroplot._patterns import RE_SPECTRUM_ROOT

def show_plots(ext: str, s: list[bool]) -> bool:
    """Check if the file type matches any requested plot type.

    Parameters
    ----------
    ext : str
        File extension (".out", ".asc", ".spectrum", or ".spectrum.rootX").
    s : list of bool
        Show flags for each plot type:
        [single_lineshape, single_lineshape_area, conv_spectrum, sticks,
         exp_spectrum, esd_spectrum, single_root_area].

    Returns
    -------
    bool
        True if the file type is needed for any active plot.
    """
    if ext == ".out":
        return s[0] or s[1] or s[2] or s[3]
    elif ext == ".asc":
        return s[4]
    elif ext == ".spectrum" or RE_SPECTRUM_ROOT.search(ext):
        return s[5] or s[6]
    return False

def is_unique(s: pd.Series) -> bool:
    """Check if all values in a Series are identical.

    An empty series trivially has all identical elements.

    Parameters
    ----------
    s : pd.Series
        The series to check.

    Returns
    -------
    bool
        True if all elements are equal or the series is empty.
    """
    a = s.to_numpy()
    if len(a) == 0:
        return True
    return bool((a[0] == a).all())

def rootSum(df: pd.DataFrame) -> pd.DataFrame:
    """Sum all ESD root spectra for a given system.

    Validates that all roots belong to the same system and share the
    same x-axis data before summing their y-data.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing ESD root data with columns
        ``root_number``, ``name``, ``xdata``, ``ydata``.

    Returns
    -------
    pd.DataFrame
        Single-row DataFrame with the summed spectrum.

    Raises
    ------
    ValueError
        If roots come from different systems or have different xdata.
    """
    data = df[df["root_number"] > 0]
    if not is_unique(data["name"]):
        raise ValueError("Roots from different systems.")
    name = data["name"].iloc[0]
    samex = [np.array_equal(data["xdata"].iloc[0], row["xdata"])
             for _,row in data.iterrows()]
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
    """Build the x-axis grid for convolution.

    The grid starts at 0 (required for peak detection) and extends to
    the maximum data point or the user-provided end value.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with an ``xdata_plot_max`` column.
    x1 : float or None
        User-defined end of the x-axis. If given and larger than the
        data maximum, it is used as the upper bound.
    npt : int
        Number of points per unit.

    Returns
    -------
    np.ndarray
        1-D array of evenly spaced x-values.
    """
    xmax_data = df["xdata_plot_max"].max()
    if x1 is not None and x1 > xmax_data:
        maxrange = x1
    else:
        maxrange = xmax_data
    return np.arange(0, maxrange, 1 / npt)

def roundup(x: float, ev_plot: bool, wn_plot: bool, nm_plot: bool) -> float:
    """Round up to the next tick interval.

    eV → next integer, cm⁻¹ → next 100, nm → next 10.

    Parameters
    ----------
    x : float
        Value to round up.
    ev_plot : bool
        Plot unit is eV.
    wn_plot : bool
        Plot unit is cm⁻¹.
    nm_plot : bool
        Plot unit is nm.

    Returns
    -------
    float
        The rounded-up value.

    Raises
    ------
    ValueError
        If no unit flag is set.
    """
    if ev_plot:
        return x if x % 1 == 0 else x + 1 - x % 1
    elif wn_plot:
        return x if x % 100 == 0 else x + 100 - x % 100
    elif nm_plot:
        return x if x % 10 == 0 else x + 10 - x % 10
    raise ValueError("No unit plot flag set")

def rounddown(x: float, ev_plot: bool, wn_plot: bool, nm_plot: bool) -> float:
    """Round down to the previous tick interval.

    eV → previous integer, cm⁻¹ → previous 100, nm → previous 10.

    Parameters
    ----------
    x : float
        Value to round down.
    ev_plot : bool
        Plot unit is eV.
    wn_plot : bool
        Plot unit is cm⁻¹.
    nm_plot : bool
        Plot unit is nm.

    Returns
    -------
    float
        The rounded-down value.

    Raises
    ------
    ValueError
        If no unit flag is set.
    """
    if ev_plot:
        return x if x % 1 == 0 else x - x % 1
    elif wn_plot:
        return x if x % 100 == 0 else x - x % 100
    elif nm_plot:
        return x if x % 10 == 0 else x - x % 10
    raise ValueError("No unit plot flag set")

def lineshape(a: float, m: np.ndarray, x: float, w: float,
              ls_gauss: bool) -> np.ndarray:
    """Compute a Gaussian or Lorentzian line shape.

    Parameters
    ----------
    a : float
        Amplitude (maximum intensity).
    m : np.ndarray
        Full x-range array over which to compute the line shape.
    x : float
        Centre position of the line (stick position).
    w : float
        Full width at half maximum (FWHM).
    ls_gauss : bool
        If True use a Gaussian line shape; otherwise Lorentzian.

    Returns
    -------
    np.ndarray
        Line shape evaluated at every point in ``m``.
    """
    if ls_gauss:
        return a * np.exp(-(np.log(2) * (2 * (m - x) / w) ** 2))
    else:
        return a / (1 + (2 * (m - x) / w) ** 2)

def normalization(x: np.ndarray) -> np.ndarray:
    """Normalise an array to the [0, 1] range.

    Parameters
    ----------
    x : np.ndarray
        Input array.

    Returns
    -------
    np.ndarray
        Normalised array. If all values are identical returns zeros.
    """
    denom = np.amax(x) - np.amin(x)
    if denom == 0:
        return np.zeros_like(x)
    return (x - np.amin(x)) / denom

def atLeastTwo(a: bool, b: bool, c: bool) -> bool:
    """Return True if at least two of three booleans are True.

    Parameters
    ----------
    a, b, c : bool
        Input booleans.

    Returns
    -------
    bool
        True if at least two inputs are True.
    """
    return a and (b or c) or (b and c)

def plotType(nm: bool, wn: bool, ev: bool) -> tuple[str, int]:
    """Return the plot type name and points-per-unit based on flags.

    The default unit is cm⁻¹ (``wn``).

    Parameters
    ----------
    nm : bool
        Plot in nanometres.
    wn : bool
        Plot in wavenumbers (cm⁻¹).
    ev : bool
        Plot in electronvolts.

    Returns
    -------
    tuple of (str, int)
        Unit label (``"nm"``, ``"wn"``, or ``"ev"``) and the
        corresponding points-per-unit constant.
    """
    if nm:
        return "nm", npt_nm
    if wn:
        return "wn", npt_wn
    if ev:
        return "ev", npt_ev
    return "wn", npt_wn

def wntonm(wn: np.ndarray) -> np.ndarray:
    """Convert wavenumber to wavelength.

    Parameters
    ----------
    wn : np.ndarray
        Wavenumber values in cm⁻¹.

    Returns
    -------
    np.ndarray
        Wavelength values in nm.
    """
    return 1e7 / np.asarray(wn)

def wntoev(wn: np.ndarray) -> np.ndarray:
    """Convert wavenumber to energy.

    Parameters
    ----------
    wn : np.ndarray
        Wavenumber values in cm⁻¹.

    Returns
    -------
    np.ndarray
        Energy values in eV.
    """
    return np.asarray(wn) / CONV_WNTOEV

def nmtown(wl: np.ndarray) -> np.ndarray:
    """Convert wavelength to wavenumber.

    Parameters
    ----------
    wl : np.ndarray
        Wavelength values in nm.

    Returns
    -------
    np.ndarray
        Wavenumber values in cm⁻¹.
    """
    return 1e7 / np.asarray(wl)

def nmtoev(wl: np.ndarray) -> np.ndarray:
    """Convert wavelength to energy.

    Parameters
    ----------
    wl : np.ndarray
        Wavelength values in nm.

    Returns
    -------
    np.ndarray
        Energy values in eV.
    """
    return 1e7 / np.asarray(wl) / CONV_WNTOEV

def unitConverter(data: np.ndarray, ext: str, unit: str) -> np.ndarray:
    """Convert x-axis data to the requested unit.

    Experimental data (``.asc``) is assumed to be in nm; all other
    types are assumed to be in cm⁻¹.

    Parameters
    ----------
    data : np.ndarray
        Input x-axis data.
    ext : str
        File extension indicating the origin of the data.
    unit : {"nm", "wn", "ev"}
        Target unit for the conversion.

    Returns
    -------
    np.ndarray
        Converted x-axis data.
    """
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
    """Convert and optionally shift the x-axis data of a spectrum.

    Experimental data is converted from nm; other data is converted
    from cm⁻¹ and shifted by the given offset.

    Parameters
    ----------
    row : pd.Series
        Row with keys ``ext`` and ``xdata``.
    unit : {"nm", "wn", "ev"}
        Target unit.
    shift : float
        Horizontal shift applied in the source unit.

    Returns
    -------
    np.ndarray
        Processed x-axis data.
    """
    ext = row["ext"]
    if ext == ".asc":
        data = row["xdata"]
    else:
        data = np.asarray(row["xdata"]) + shift
    return unitConverter(data, ext, unit)

def xdatamin(row: pd.Series, w: float) -> float:
    """Return the minimum x-axis value for a spectrum row.

    For experimental data the minimum is shifted left by ``3 * w`` to
    accommodate line broadening.

    Parameters
    ----------
    row : pd.Series
        Row with keys ``ext`` and ``xdata_plot``.
    w : float
        Line width (FWHM).

    Returns
    -------
    float
        Minimum x-axis value.
    """
    ext = row["ext"]
    data = row["xdata_plot"]
    if ext == ".asc":
        return min(data) - w * 3
    else:
        return min(data)

def xdatamax(row: pd.Series, w: float) -> float:
    """Return the maximum x-axis value for a spectrum row.

    For experimental data the maximum is shifted right by ``3 * w`` to
    accommodate line broadening.

    Parameters
    ----------
    row : pd.Series
        Row with keys ``ext`` and ``xdata_plot``.
    w : float
        Line width (FWHM).

    Returns
    -------
    float
        Maximum x-axis value.
    """
    ext = row["ext"]
    data = row["xdata_plot"]
    if ext == ".asc":
        return max(data) + w * 3
    else:
        return max(data)
