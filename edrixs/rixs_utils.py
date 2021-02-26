__all__ = ['scattering_mat']

import numpy as np


def scattering_mat(eval_i, eval_n, trans_mat_abs,
                   trans_mat_emi, omega_inc, gamma_n):

    num_gs = trans_mat_abs.shape[2]
    num_ex = trans_mat_abs.shape[1]
    num_fs = trans_mat_emi.shape[1]

    npol_abs = trans_mat_abs.shape[0]
    npol_emi = trans_mat_emi.shape[0]

    Ffi = np.zeros((npol_emi, npol_abs, num_fs, num_gs), dtype=np.complex128)
    tmp_abs = np.zeros((npol_abs, num_ex, num_gs), dtype=np.complex128)
    denomi = np.zeros((num_ex, num_gs), dtype=np.complex128)

    for i in range(num_ex):
        for j in range(num_gs):
            aa = omega_inc - (eval_n[i] - eval_i[j])
            denomi[i, j] = 1.0 / (aa + 1j * gamma_n)

    for i in range(npol_abs):
        tmp_abs[i] = trans_mat_abs[i] * denomi

    for i in range(npol_emi):
        for j in range(npol_abs):
            Ffi[i, j, :, :] = np.dot(trans_mat_emi[i], tmp_abs[j])

    return Ffi
