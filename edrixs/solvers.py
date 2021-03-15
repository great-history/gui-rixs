__all__ = ['ed_1v1c_py', 'xas_1v1c_py', 'rixs_1v1c_py']

import numpy as np
from scipy import linalg

from .iostream import (
    write_tensor, write_emat, write_umat, write_config, read_poles_from_file
)
from .angular_momentum import (
    get_sx, get_sy, get_sz, get_lx, get_ly, get_lz, rmat_to_euler, get_wigner_dmat
)
from .photon_transition import (
    get_trans_oper, quadrupole_polvec, dipole_polvec_xas, dipole_polvec_rixs, unit_wavevector
)
from .coulomb_utensor import get_umat_slater, get_umat_slater_3shells
from .manybody_operator import two_fermion, four_fermion
from .fock_basis import get_fock_bin_by_N, write_fock_dec_by_N
from .basis_transform import cb_op2, tmat_r2c, cb_op
from .utils import info_atomic_shell, slater_integrals_name, boltz_dist
from .rixs_utils import scattering_mat
from .plot_spectrum import get_spectra_from_poles, merge_pole_dicts
from .soc import atom_hsoc


def ed_1v1c_py(shell_name, *, shell_level=None, v_soc=None, c_soc=0,
               v_noccu=1, slater=None, ext_B=None, on_which='spin',
               v_cfmat=None, v_othermat=None, loc_axis=None, verbose=0):

    print("edrixs >>> Running ED ...")
    v_name_options = ['s', 'p', 't2g', 'd', 'f']
    c_name_options = ['s', 'p', 'p12', 'p32', 't2g', 'd', 'd32', 'd52', 'f', 'f52', 'f72']
    v_name = shell_name[0].strip()
    c_name = shell_name[1].strip()
    if v_name not in v_name_options:
        raise Exception("NOT supported type of valence shell: ", v_name)
    if c_name not in c_name_options:
        raise Exception("NOT supported type of core shell: ", c_name)

    info_shell = info_atomic_shell()

    # Quantum numbers of angular momentum
    v_orbl = info_shell[v_name][0]

    # number of orbitals including spin degree of freedom
    v_norb = info_shell[v_name][1]
    c_norb = info_shell[c_name][1]

    # total number of orbitals
    ntot = v_norb + c_norb

    emat_i = np.zeros((ntot, ntot), dtype=np.complex)
    emat_n = np.zeros((ntot, ntot), dtype=np.complex)

    # Coulomb interaction
    # Get the names of all the required slater integrals
    slater_name = slater_integrals_name((v_name, c_name), ('v', 'c'))
    nslat = len(slater_name)

    slater_i = np.zeros(nslat, dtype=np.float)
    slater_n = np.zeros(nslat, dtype=np.float)

    if slater is not None:
        if nslat > len(slater[0]):
            slater_i[0:len(slater[0])] = slater[0]
        else:
            slater_i[:] = slater[0][0:nslat]
        if nslat > len(slater[1]):
            slater_n[0:len(slater[1])] = slater[1]
        else:
            slater_n[:] = slater[1][0:nslat]

    # print summary of slater integrals
    print()
    print("    Summary of Slater integrals:")
    print("    ------------------------------")
    print("    Terms,   Initial Hamiltonian,  Intermediate Hamiltonian")
    for i in range(nslat):
        print("    ", slater_name[i], ":  {:20.10f}{:20.10f}".format(slater_i[i], slater_n[i]))
    print()

    case = v_name + c_name
    umat_i = get_umat_slater(case, *slater_i)
    umat_n = get_umat_slater(case, *slater_n)

    if verbose > 0:
        write_umat(umat_i, 'coulomb_i.in')
        write_umat(umat_n, 'coulomb_n.in')

    # SOC
    if v_soc is not None:
        emat_i[0:v_norb, 0:v_norb] += atom_hsoc(v_name, v_soc[0])
        emat_n[0:v_norb, 0:v_norb] += atom_hsoc(v_name, v_soc[1])

    # when the core-shell is any of p12, p32, d32, d52, f52, f72,
    # do not need to add SOC for core shell
    if c_name in ['p', 'd', 'f']:
        emat_n[v_norb:ntot, v_norb:ntot] += atom_hsoc(c_name, c_soc)

    # crystal field
    if v_cfmat is not None:
        emat_i[0:v_norb, 0:v_norb] += np.array(v_cfmat)
        emat_n[0:v_norb, 0:v_norb] += np.array(v_cfmat)

    # other hopping matrix
    if v_othermat is not None:
        emat_i[0:v_norb, 0:v_norb] += np.array(v_othermat)
        emat_n[0:v_norb, 0:v_norb] += np.array(v_othermat)

    # energy of shells
    if shell_level is not None:
        emat_i[0:v_norb, 0:v_norb] += np.eye(v_norb) * shell_level[0]
        emat_i[v_norb:ntot, v_norb:ntot] += np.eye(c_norb) * shell_level[1]
        emat_n[0:v_norb, 0:v_norb] += np.eye(v_norb) * shell_level[0]
        emat_n[v_norb:ntot, v_norb:ntot] += np.eye(c_norb) * shell_level[1]

    # external magnetic field
    if v_name == 't2g':
        lx, ly, lz = get_lx(1, True), get_ly(1, True), get_lz(1, True)
        sx, sy, sz = get_sx(1), get_sy(1), get_sz(1)
        lx, ly, lz = -lx, -ly, -lz
    else:
        lx, ly, lz = get_lx(v_orbl, True), get_ly(v_orbl, True), get_lz(v_orbl, True)
        sx, sy, sz = get_sx(v_orbl), get_sy(v_orbl), get_sz(v_orbl)

    if ext_B is not None:
        if on_which.strip() == 'spin':
            zeeman = ext_B[0] * (2 * sx) + ext_B[1] * (2 * sy) + ext_B[2] * (2 * sz)
        elif on_which.strip() == 'orbital':
            zeeman = ext_B[0] * lx + ext_B[1] * ly + ext_B[2] * lz
        elif on_which.strip() == 'both':
            zeeman = ext_B[0] * (lx + 2 * sx) + ext_B[1] * (ly + 2 * sy) + ext_B[2] * (lz + 2 * sz)
        else:
            raise Exception("Unknown value of on_which", on_which)
        emat_i[0:v_norb, 0:v_norb] += zeeman
        emat_n[0:v_norb, 0:v_norb] += zeeman

    if verbose > 0:
        write_emat(emat_i, 'hopping_i.in')
        write_emat(emat_n, 'hopping_n.in')

    basis_i = get_fock_bin_by_N(v_norb, v_noccu, c_norb, c_norb)
    basis_n = get_fock_bin_by_N(v_norb, v_noccu+1, c_norb, c_norb - 1)
    ncfg_i, ncfg_n = len(basis_i), len(basis_n)
    print("edrixs >>> Dimension of the initial Hamiltonian: ", ncfg_i)
    print("edrixs >>> Dimension of the intermediate Hamiltonian: ", ncfg_n)

    # Build many-body Hamiltonian in Fock basis
    print("edrixs >>> Building Many-body Hamiltonians ...")
    hmat_i = np.zeros((ncfg_i, ncfg_i), dtype=np.complex)
    hmat_n = np.zeros((ncfg_n, ncfg_n), dtype=np.complex)
    hmat_i[:, :] += two_fermion(emat_i, basis_i, basis_i)
    hmat_i[:, :] += four_fermion(umat_i, basis_i)
    hmat_n[:, :] += two_fermion(emat_n, basis_n, basis_n)
    hmat_n[:, :] += four_fermion(umat_n, basis_n)
    print("edrixs >>> Done !")

    # Do exact-diagonalization to get eigenvalues and eigenvectors
    print("edrixs >>> Exact Diagonalization of Hamiltonians ...")
    print(hmat_i)
    print(hmat_n)
    print(type(hmat_i))
    eval_i, evec_i = linalg.eigh(hmat_i)
    print("whose problem")
    eval_n, evec_n = linalg.eigh(hmat_n)
    print("edrixs >>> Done !")

    if verbose > 0:
        write_tensor(eval_i, 'eval_i.dat')
        write_tensor(eval_n, 'eval_n.dat')

    # Build dipolar transition operators in local-xyz axis
    if loc_axis is not None:
        local_axis = np.array(loc_axis)
    else:
        local_axis = np.eye(3)
    tmp = get_trans_oper(case)
    npol, n, m = tmp.shape
    tmp_g = np.zeros((npol, n, m), dtype=np.complex)
    # Transform the transition operators to global-xyz axis
    # dipolar transition
    if npol == 3:
        for i in range(3):
            for j in range(3):
                tmp_g[i] += local_axis[i, j] * tmp[j]

    # quadrupolar transition
    elif npol == 5:
        alpha, beta, gamma = rmat_to_euler(local_axis)
        wignerD = get_wigner_dmat(4, alpha, beta, gamma)
        rotmat = np.dot(np.dot(tmat_r2c('d'), wignerD), np.conj(np.transpose(tmat_r2c('d'))))
        for i in range(5):
            for j in range(5):
                tmp_g[i] += rotmat[i, j] * tmp[j]
    else:
        raise Exception("Have NOT implemented this case: ", npol)

    tmp2 = np.zeros((npol, ntot, ntot), dtype=np.complex)
    trans_op = np.zeros((npol, ncfg_n, ncfg_i), dtype=np.complex)
    for i in range(npol):
        tmp2[i, 0:v_norb, v_norb:ntot] = tmp_g[i]
        trans_op[i] = two_fermion(tmp2[i], basis_n, basis_i)
        trans_op[i] = cb_op2(trans_op[i], evec_n, evec_i)

    print("edrixs >>> ED Done !")

    return eval_i, eval_n, trans_op


def xas_1v1c_py(eval_i, eval_n, trans_op, ominc, *, gamma_c=0.1, thin=1.0, phi=0,
                pol_type=None, gs_list=None, temperature=1.0, scatter_axis=None):

    print("edrixs >>> Running XAS ...")
    n_om = len(ominc)
    npol, ncfg_n = trans_op.shape[0], trans_op.shape[1]
    if pol_type is None:
        pol_type = [('isotropic', 0)]
    if gs_list is None:
        gs_list = [0]
    if scatter_axis is None:
        scatter_axis = np.eye(3)
    else:
        scatter_axis = np.array(scatter_axis)

    xas = np.zeros((n_om, len(pol_type)), dtype=np.float)
    gamma_core = np.zeros(n_om, dtype=np.float)
    prob = boltz_dist([eval_i[i] for i in gs_list], temperature)
    if np.isscalar(gamma_c):
        gamma_core[:] = np.ones(n_om) * gamma_c
    else:
        gamma_core[:] = gamma_c

    kvec = unit_wavevector(thin, phi, scatter_axis, 'in')
    for i, om in enumerate(ominc):
        for it, (pt, alpha) in enumerate(pol_type):
            if pt.strip() not in ['left', 'right', 'linear', 'isotropic']:
                raise Exception("Unknown polarization type: ", pt)
            polvec = np.zeros(npol, dtype=np.complex)
            if pt.strip() == 'left' or pt.strip() == 'right' or pt.strip() == 'linear':
                pol = dipole_polvec_xas(thin, phi, alpha, scatter_axis, pt)
                if npol == 3:  # dipolar transition
                    polvec[:] = pol
                if npol == 5:  # quadrupolar transition
                    polvec[:] = quadrupole_polvec(pol, kvec)

            # loop over all the initial states
            for j, igs in enumerate(gs_list):
                if pt.strip() == 'isotropic':
                    for k in range(npol):
                        xas[i, it] += (
                            prob[j] * np.sum(np.abs(trans_op[k, :, igs])**2 * gamma_core[i] /
                                             np.pi / ((om - (eval_n[:] - eval_i[igs]))**2 +
                                             gamma_core[i]**2))
                        )
                    xas[i, it] = xas[i, it] / npol
                else:
                    F_mag = np.zeros(ncfg_n, dtype=np.complex)
                    for k in range(npol):
                        F_mag += trans_op[k, :, igs] * polvec[k]
                    xas[i, it] += (
                        prob[j] * np.sum(np.abs(F_mag)**2 * gamma_core[i] / np.pi /
                                         ((om - (eval_n[:] - eval_i[igs]))**2 + gamma_core[i]**2))
                    )

    print("edrixs >>> XAS Done !")

    return xas


def rixs_1v1c_py(eval_i, eval_n, trans_op, ominc, eloss, *,
                 gamma_c=0.1, gamma_f=0.01, thin=1.0, thout=1.0, phi=0.0,
                 pol_type=None, gs_list=None, temperature=1.0, scatter_axis=None):

    print("edrixs >>> Running RIXS ... ")
    n_ominc = len(ominc)
    n_eloss = len(eloss)
    gamma_core = np.zeros(n_ominc, dtype=np.float)
    gamma_final = np.zeros(n_eloss, dtype=np.float)
    if np.isscalar(gamma_c):
        gamma_core[:] = np.ones(n_ominc) * gamma_c
    else:
        gamma_core[:] = gamma_c

    if np.isscalar(gamma_f):
        gamma_final[:] = np.ones(n_eloss) * gamma_f
    else:
        gamma_final[:] = gamma_f

    if pol_type is None:
        pol_type = [('linear', 0, 'linear', 0)]
    if gs_list is None:
        gs_list = [0]
    if scatter_axis is None:
        scatter_axis = np.eye(3)
    else:
        scatter_axis = np.array(scatter_axis)

    prob = boltz_dist([eval_i[i] for i in gs_list], temperature)
    rixs = np.zeros((len(ominc), len(eloss), len(pol_type)), dtype=np.float)
    npol, n, m = trans_op.shape
    trans_emi = np.zeros((npol, m, n), dtype=np.complex128)
    for i in range(npol):
        trans_emi[i] = np.conj(np.transpose(trans_op[i]))
    polvec_i = np.zeros(npol, dtype=np.complex)
    polvec_f = np.zeros(npol, dtype=np.complex)

    # Calculate RIXS
    for i, om in enumerate(ominc):
        F_fi = scattering_mat(eval_i, eval_n, trans_op[:, :, 0:max(gs_list)+1],
                              trans_emi, om, gamma_core[i])
        for j, (it, alpha, jt, beta) in enumerate(pol_type):
            ei, ef = dipole_polvec_rixs(thin, thout, phi, alpha, beta,
                                        scatter_axis, (it, jt))
            # dipolar transition
            if npol == 3:
                polvec_i[:] = ei
                polvec_f[:] = ef
            # quadrupolar transition
            elif npol == 5:
                ki = unit_wavevector(thin, phi, scatter_axis, direction='in')
                kf = unit_wavevector(thout, phi, scatter_axis, direction='out')
                polvec_i[:] = quadrupole_polvec(ei, ki)
                polvec_f[:] = quadrupole_polvec(ef, kf)
            else:
                raise Exception("Have NOT implemented this type of transition operators")
            # scattering magnitude with polarization vectors
            F_mag = np.zeros((len(eval_i), len(gs_list)), dtype=np.complex)
            for m in range(npol):
                for n in range(npol):
                    F_mag[:, :] += np.conj(polvec_f[m]) * F_fi[m, n] * polvec_i[n]
            for m, igs in enumerate(gs_list):
                for n in range(len(eval_i)):
                    rixs[i, :, j] += (
                        prob[m] * np.abs(F_mag[n, igs])**2 * gamma_final / np.pi /
                        ((eloss - (eval_i[n] - eval_i[igs]))**2 + gamma_final**2)
                    )
    print("edrixs >>> RIXS Done !")

    return rixs

