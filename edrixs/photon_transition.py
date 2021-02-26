__all__ = ['dipole_trans_oper', 'quadrupole_trans_oper', 'get_trans_oper',
           'unit_wavevector', 'wavevector_with_length', 'get_wavevector_rixs',
           'linear_polvec', 'dipole_polvec_rixs', 'dipole_polvec_xas',
           'quadrupole_polvec']

import numpy as np
from sympy.physics.wigner import clebsch_gordan
from .basis_transform import tmat_c2r, tmat_r2c, tmat_c2j, cb_op2
from .utils import case_to_shell_name, info_atomic_shell


def dipole_trans_oper(l1, l2):
    from sympy import N

    n1, n2 = 2 * l1 + 1, 2 * l2 + 1
    op = np.zeros((3, n1, n2), dtype=np.complex128)
    for i1, m1 in enumerate(range(-l1, l1 + 1)):
        for i2, m2 in enumerate(range(-l2, l2 + 1)):
            tmp1 = clebsch_gordan(l2, 1, l1, m2, -1, m1)
            tmp2 = clebsch_gordan(l2, 1, l1, m2, 1, m1)
            tmp3 = clebsch_gordan(l2, 1, l1, m2, 0, m1)
            tmp1, tmp2, tmp3 = N(tmp1), N(tmp2), N(tmp3)
            op[0, i1, i2] = (tmp1 - tmp2) * np.sqrt(2.0) / 2.0
            op[1, i1, i2] = (tmp1 + tmp2) * 1j * np.sqrt(2.0) / 2.0
            op[2, i1, i2] = tmp3
    op_spin = np.zeros((3, 2 * n1, 2 * n2), dtype=np.complex128)
    for i in range(3):
        op_spin[i, 0:2 * n1:2, 0:2 * n2:2] = op[i]
        op_spin[i, 1:2 * n1:2, 1:2 * n2:2] = op[i]

    return op_spin


def quadrupole_trans_oper(l1, l2):
    from sympy import N
    n1, n2 = 2 * l1 + 1, 2 * l2 + 1
    op = np.zeros((5, n1, n2), dtype=np.complex128)
    for i1, m1 in enumerate(range(-l1, l1 + 1)):
        for i2, m2 in enumerate(range(-l2, l2 + 1)):
            t1 = clebsch_gordan(l2, 2, l1, m2, -2, m1)
            t2 = clebsch_gordan(l2, 2, l1, m2, 2, m1)
            t3 = clebsch_gordan(l2, 2, l1, m2, 0, m1)
            t4 = clebsch_gordan(l2, 2, l1, m2, -1, m1)
            t5 = clebsch_gordan(l2, 2, l1, m2, 1, m1)
            t1, t2, t3, t4, t5 = N(t1), N(t2), N(t3), N(t4), N(t5)

            op[0, i1, i2] = t3
            op[1, i1, i2] = (t4 - t5) / np.sqrt(2.0)
            op[2, i1, i2] = (t4 + t5) * 1j / np.sqrt(2.0)
            op[3, i1, i2] = (t1 + t2) / np.sqrt(2.0)
            op[4, i1, i2] = (t1 - t2) * 1j / np.sqrt(2.0)

    op_spin = np.zeros((5, 2 * n1, 2 * n2), dtype=np.complex128)
    for i in range(5):
        op_spin[i, 0:2 * n1:2, 0:2 * n2:2] = op[i]
        op_spin[i, 1:2 * n1:2, 1:2 * n2:2] = op[i]

    return op_spin


def get_trans_oper(case):

    info = info_atomic_shell()
    v_name, c_name = case_to_shell_name(case.strip())
    v_orbl, c_orbl = info[v_name][0], info[c_name][0]
    v_norb, c_norb = 2 * (2 * v_orbl + 1), 2 * (2 * c_orbl + 1)
    if (v_orbl + c_orbl) % 2 == 0:
        op = quadrupole_trans_oper(v_orbl, c_orbl)
    else:
        op = dipole_trans_oper(v_orbl, c_orbl)

    # truncate to a sub-shell if necessary
    special_shell = ['t2g', 'p12', 'p32', 'd32', 'd52', 'f52', 'f72']
    orb_indx = {
        special_shell[0]: [2, 3, 4, 5, 8, 9],
        special_shell[1]: [0, 1],
        special_shell[2]: [2, 3, 4, 5],
        special_shell[3]: [0, 1, 2, 3],
        special_shell[4]: [4, 5, 6, 7, 8, 9],
        special_shell[5]: [0, 1, 2, 3, 4, 5],
        special_shell[6]: [6, 7, 8, 9, 10, 11, 12, 13]
    }
    left_tmat = np.eye(v_norb, dtype=np.complex)
    right_tmat = np.eye(c_norb, dtype=np.complex)
    indx1 = list(range(0, v_norb))
    indx2 = list(range(0, c_norb))
    if v_name in special_shell:
        if v_name == 't2g':
            left_tmat[0:v_norb, 0:v_norb] = tmat_c2r('d', True)
        else:
            left_tmat[0:v_norb, 0:v_norb] = tmat_c2j(v_orbl)
        indx1 = orb_indx[v_name]
    if c_name in special_shell[1:]:
        right_tmat[0:c_norb, 0:c_norb] = tmat_c2j(c_orbl)
        indx2 = orb_indx[c_name]

    if (v_orbl + c_orbl) % 2 == 0:
        npol = 5
    else:
        npol = 3

    op_tmp = np.zeros((npol, len(indx1), len(indx2)), dtype=np.complex)
    for i in range(npol):
        op[i] = cb_op2(op[i], left_tmat, right_tmat)
        op_tmp[i] = op[i, indx1][:, indx2]
        if v_name == 't2g':
            op_tmp[i] = np.dot(np.conj(np.transpose(tmat_r2c('t2g', True))), op_tmp[i])
    res = op_tmp
    return res


def unit_wavevector(theta, phi, local_axis=None, direction='in'):

    if local_axis is None:
        local_axis = np.eye(3)
    else:
        local_axis = np.array(local_axis)

    if direction.strip() == 'in':
        unit_k = np.array([-np.cos(theta) * np.cos(phi),
                           -np.cos(theta) * np.sin(phi),
                           -np.sin(theta)])
        unit_k = np.dot(local_axis, unit_k)
    elif direction.strip() == 'out':
        unit_k = np.array([-np.cos(theta) * np.cos(phi),
                           -np.cos(theta) * np.sin(phi),
                           np.sin(theta)])
        unit_k = np.dot(local_axis, unit_k)
    else:
        raise Exception("Unknown direction in unit_wavevector: ", direction)

    return unit_k


def wavevector_with_length(theta, phi, energy, local_axis=None, direction='in'):

    hbarc = 1.973270533 * 1000  # eV*A
    k_len = energy / hbarc
    if local_axis is None:
        local_axis = np.eye(3)
    else:
        local_axis = np.array(local_axis)

    k_with_length = k_len * unit_wavevector(theta, phi, local_axis, direction)

    return k_with_length


def get_wavevector_rixs(thin, thout, phi, ein, eout, local_axis=None):

    if local_axis is None:
        local_axis = np.eye(3)
    else:
        local_axis = np.array(local_axis)

    k_in_global = wavevector_with_length(thin, phi, ein, local_axis, direction='in')
    k_out_global = wavevector_with_length(thout, phi, eout, local_axis, direction='out')

    return k_in_global, k_out_global


def linear_polvec(theta, phi, alpha, local_axis=None, direction='in'):

    if local_axis is None:
        local_axis = np.eye(3)
    else:
        local_axis = np.array(local_axis)

    if direction.strip() == 'in':
        polvec = (
            np.array([-np.cos(phi) * np.cos(np.pi / 2.0 - theta),
                      -np.sin(phi) * np.cos(np.pi / 2.0 - theta),
                      +np.sin(np.pi / 2.0 - theta)]) * np.cos(alpha) +
            np.array([-np.sin(phi), np.cos(phi), 0]) * np.sin(alpha)
        )
        polvec = np.dot(local_axis, polvec)
    elif direction.strip() == 'out':
        polvec = (
            np.array([+np.cos(phi) * np.cos(np.pi / 2.0 - theta),
                      +np.sin(phi) * np.cos(np.pi / 2.0 - theta),
                      +np.sin(np.pi / 2.0 - theta)]) * np.cos(alpha) +
            np.array([-np.sin(phi), np.cos(phi), 0]) * np.sin(alpha)
        )
        polvec = np.dot(local_axis, polvec)
    else:
        raise Exception("Unknown direction in linear_polvec: ", direction)

    return polvec


def dipole_polvec_rixs(thin, thout, phi=0, alpha=0, beta=0, local_axis=None, pol_type=None):

    if local_axis is None:
        local_axis = np.eye(3)
    else:
        local_axis = np.array(local_axis)

    if pol_type is None:
        pol_type = ('linear', 'linear')

    ex = linear_polvec(thin, phi, 0, local_axis, direction='in')
    ey = linear_polvec(thin, phi, np.pi/2.0, local_axis, direction='in')
    if pol_type[0].strip() == 'linear':
        ei_global = linear_polvec(thin, phi, alpha, local_axis, direction='in')
    elif pol_type[0].strip() == 'left':
        ei_global = (ex + 1j * ey) / np.sqrt(2.0)
    elif pol_type[0].strip() == 'right':
        ei_global = (ex - 1j * ey) / np.sqrt(2.0)
    else:
        raise Exception("Unknown polarization type for incident photon: ", pol_type[0])

    ex = linear_polvec(thout, phi, 0, local_axis, direction='out')
    ey = linear_polvec(thout, phi, np.pi/2.0, local_axis, direction='out')
    if pol_type[1].strip() == 'linear':
        ef_global = linear_polvec(thout, phi, beta, local_axis, direction='out')
    elif pol_type[1].strip() == 'left':
        ef_global = (ex + 1j * ey) / np.sqrt(2.0)
    elif pol_type[1].strip() == 'right':
        ef_global = (ex - 1j * ey) / np.sqrt(2.0)
    else:
        raise Exception("Unknown polarization type for scattered photon: ", pol_type[1])

    return ei_global, ef_global


def dipole_polvec_xas(thin, phi=0, alpha=0, local_axis=None, pol_type='linear'):

    if local_axis is None:
        local_axis = np.eye(3)
    else:
        local_axis = np.array(local_axis)

    ex = linear_polvec(thin, phi, 0, local_axis, direction='in')
    ey = linear_polvec(thin, phi, np.pi/2.0, local_axis, direction='in')
    if pol_type.strip() == 'linear':
        ei_global = linear_polvec(thin, phi, alpha, local_axis, direction='in')
    elif pol_type.strip() == 'left':
        ei_global = (ex + 1j * ey) / np.sqrt(2.0)
    elif pol_type.strip() == 'right':
        ei_global = (ex - 1j * ey) / np.sqrt(2.0)
    else:
        raise Exception("Unknown polarization type for incident photon: ", pol_type)

    return ei_global


def quadrupole_polvec(polvec, wavevec):

    quad_vec = np.zeros(5, dtype=np.complex)
    kvec = wavevec / np.sqrt(np.dot(wavevec, wavevec))

    quad_vec[0] = 0.5 * (2 * polvec[2] * kvec[2] - polvec[0] * kvec[0] - polvec[1] * kvec[1])
    quad_vec[1] = np.sqrt(3.0)/2.0 * (polvec[2] * kvec[0] + polvec[0] * kvec[2])
    quad_vec[2] = np.sqrt(3.0)/2.0 * (polvec[1] * kvec[2] + polvec[2] * kvec[1])
    quad_vec[3] = np.sqrt(3.0)/2.0 * (polvec[0] * kvec[0] - polvec[1] * kvec[1])
    quad_vec[4] = np.sqrt(3.0)/2.0 * (polvec[0] * kvec[1] + polvec[1] * kvec[0])

    return quad_vec
