import glob
import numpy as np
import matplotlib.ticker as mticker
import math

def get_data_paths(data_path, run_nmr, type):
    """Return a list of files in data_path/run_number/RAW with type extension"""
    paths = glob.glob(f"{data_path}/run_25_06_2024_{run_nmr}/RAW/*.{type}")
    paths.sort()
    return paths

def rebin_histogram(weights, edges, n):
    """Given a histogram weights and edges, return a rebinned histogram of bins = ceil(len(weights) / n)"""

    new_weights = None
    if len(weights) % n == 0:
        new_weights = weights.reshape(-1, n).sum(axis=-1)
    else:
        new_weights = np.zeros(len(weights) // n * n + n)
        new_weights[:len(weights)] = weights
        new_weights = new_weights.reshape(-1, n).sum(axis=-1)
    new_edges = edges[::n]
    if len(new_edges) == len(new_weights):
        new_edges = np.concatenate((new_edges, [new_edges[-1] + n]))
    else:
        new_edges = new_edges[:len(new_weights)+1]
    return new_weights, new_edges


# Extract scientific notations for plot labeling
f = mticker.ScalarFormatter(useOffset=False, useMathText=True)
dx = None

def extract_scientific_notation(x, dx):
    exponent = np.log10(np.abs(x))
    dexponent = np.log10(np.abs(dx))

    if exponent in (-np.inf, np.inf):
        exponent = 0
    if dexponent in (-np.inf, np.inf):
        dexponent = exponent - 1

    exponent = np.ceil(exponent)
    dexponent = np.ceil(dexponent)
    
    dexponent = int(dexponent - 2)
    uncertainty = int(np.round(dx / 10**dexponent))

    exponent = int(exponent - 1)
    num_decimals = exponent - dexponent
    num_value = np.round(x / 10**exponent, num_decimals)

    return num_value, uncertainty, exponent, num_decimals

def format_sci_notation(num_value, uncertainty, exponent, num_decimals):
    if exponent in (0, 1, 2):
        if len(str(np.abs(num_value))) - 2 == num_decimals:
            out = r"${0}({1})$".format(np.round(num_value * 10**exponent, num_decimals - exponent), uncertainty)
        else:
            num_value_str = str(np.round(num_value * 10**exponent, num_decimals - exponent))
            for _ in range(num_decimals - len(str(np.abs(num_value))) + 2):
                num_value_str += "0"
            out = r"${0}({1})$".format(num_value_str, uncertainty)
        return out

    if len(str(np.abs(num_value))) - 2 == num_decimals:
        out = r"${0}({1})\times10^{{{2}}}$".format(num_value, uncertainty, exponent)
    else:
        num_value_str = str(num_value)
        for _ in range(num_decimals - len(str(np.abs(num_value))) + 2):
            num_value_str += "0"
        out = r"${0}({1})\times10^{{{2}}}$".format(num_value_str, uncertainty, exponent)
    return out

def g(x, pos):
    if x == 0:
        return "$0$"
    num_value, uncertainty, exponent, num_decimals = extract_scientific_notation(x, dx)
    return format_sci_notation(num_value, uncertainty, exponent, num_decimals)
fmt = mticker.FuncFormatter(g)
