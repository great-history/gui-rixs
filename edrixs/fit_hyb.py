__all__ = ['fit_func', 'fit_hyb', 'get_hyb']

import numpy as np
from scipy.optimize import curve_fit


def fit_func(x, *args):

    m = len(x) // 2
    n = len(args) // 2
    y = np.zeros(len(x), dtype=np.float64)

    tmp_x = np.zeros(m, dtype=np.complex128)
    tmp_y = np.zeros(m, dtype=np.complex128)
    tmp_x[:] = x[0:m] + 1j * x[m:2 * m]

    for i in range(n):
        tmp_y[:] += args[n + i]**2 / (tmp_x[:] - args[i])

    y[0:m] = tmp_y.real
    y[m:2 * m] = tmp_y.imag

    return y


def fit_hyb(x, y, N, p0):

    m = len(x)
    xdata = np.zeros(2 * m, dtype=np.float64)
    ydata = np.zeros(2 * m, dtype=np.float64)
    xdata[0:m], xdata[m:2 * m] = x.real, x.imag
    ydata[0:m], ydata[m:2 * m] = y.real, y.imag
    popt, pcov = curve_fit(fit_func, xdata, ydata, p0)
    e, v = popt[0:N], popt[N:2 * N]
    return e, v


def get_hyb(x, e, v):

    y = np.zeros(len(x), dtype=np.complex128)
    for i in range(len(e)):
        y[:] += v[i]**2 / (x[:] - e[i])
    return y
