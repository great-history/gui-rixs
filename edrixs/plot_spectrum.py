__all__ = ['get_spectra_from_poles', 'merge_pole_dicts', 'plot_spectrum', 'plot_rixs_map']

import numpy as np
import matplotlib.pyplot as plt
from .utils import boltz_dist
from .iostream import read_poles_from_file


def get_spectra_from_poles(poles_dict, omega_mesh, gamma_mesh, temperature):

    nom = len(omega_mesh)
    spectra = np.zeros(nom, dtype=np.float64)
    gs_dist = boltz_dist(poles_dict['eigval'], temperature)
    ngs = len(poles_dict['eigval'])
    for i in range(ngs):
        tmp_vec = np.zeros(nom, dtype=np.complex)
        neff = poles_dict['npoles'][i]
        alpha = poles_dict['alpha'][i]
        beta = poles_dict['beta'][i]
        eigval = poles_dict['eigval'][i]
        norm = poles_dict['norm'][i]
        for j in range(neff-1, 0, -1):
            tmp_vec = (
                beta[j-1]**2 / (omega_mesh + 1j * gamma_mesh + eigval - alpha[j] - tmp_vec)
            )
        tmp_vec = (
            1.0 / (omega_mesh + 1j * gamma_mesh + eigval - alpha[0] - tmp_vec)
        )
        spectra[:] += -1.0 / np.pi * np.imag(tmp_vec) * norm * gs_dist[i]

    return spectra


def merge_pole_dicts(list_pole_dict):

    new_pole_dict = {
        'eigval': [],
        'npoles': [],
        'norm': [],
        'alpha': [],
        'beta': []
    }
    for poles_dict in list(list_pole_dict):
        new_pole_dict['eigval'].extend(poles_dict['eigval'])
        new_pole_dict['npoles'].extend(poles_dict['npoles'])
        new_pole_dict['norm'].extend(poles_dict['norm'])
        new_pole_dict['alpha'].extend(poles_dict['alpha'])
        new_pole_dict['beta'].extend(poles_dict['beta'])

    return new_pole_dict


def plot_spectrum(file_list, omega_mesh, gamma_mesh, T=1.0, fname='spectrum.dat',
                  om_shift=0.0, fmt_float='{:.15f}'):

    pole_dict = read_poles_from_file(file_list)
    spectrum = get_spectra_from_poles(pole_dict, omega_mesh, gamma_mesh, T)

    space = "  "
    fmt_string = (fmt_float + space) * 2 + '\n'
    f = open(fname, 'w')
    for i in range(len(omega_mesh)):
        f.write(fmt_string.format(omega_mesh[i] + om_shift, spectrum[i]))
    f.close()


def plot_rixs_map(rixs_data, ominc_mesh, eloss_mesh, fname='rixsmap.pdf'):

    fig, ax = plt.subplots()
    a, b, c, d = min(eloss_mesh), max(eloss_mesh), min(ominc_mesh), max(ominc_mesh)
    m, n = np.array(rixs_data).shape
    if len(ominc_mesh) == m and len(eloss_mesh) == n:
        plt.imshow(
            rixs_data, extent=[a, b, c, d], origin='lower', aspect='auto',
            cmap='rainbow', interpolation='gaussian'
        )
        plt.xlabel(r'Energy loss (eV)')
        plt.ylabel(r'Energy of incident photon (eV)')
    elif len(eloss_mesh) == m and len(ominc_mesh) == n:
        plt.imshow(
            rixs_data, extent=[c, d, a, b], origin='lower', aspect='auto',
            cmap='rainbow', interpolation='gaussian'
        )
        plt.ylabel(r'Energy loss (eV)')
        plt.xlabel(r'Energy of incident photon (eV)')
    else:
        raise Exception(
            "Dimension of rixs_data is not consistent with ominc_mesh or eloss_mesh"
        )

    plt.savefig(fname)
