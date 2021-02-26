__all__ = ['one_fermion_annihilation', 'two_fermion', 'four_fermion',
           'build_opers', 'density_matrix']

import numpy as np
from collections import defaultdict


def one_fermion_annihilation(iorb, lb, rb):

    lb, rb = np.array(lb), np.array(rb)
    nr, nl, norbs = len(rb), len(lb), len(rb[0])
    indx = defaultdict(lambda: -1)
    for i, j in enumerate(lb):
        indx[tuple(j)] = i

    hmat = np.zeros((nl, nr), dtype=np.complex128)
    tmp_basis = np.zeros(norbs)
    for icfg in range(nr):
        tmp_basis[:] = rb[icfg]
        if tmp_basis[iorb] == 0:
            continue
        else:
            sign = (-1)**np.count_nonzero(tmp_basis[0:iorb])
            tmp_basis[iorb] = 0
        jcfg = indx[tuple(tmp_basis)]
        if jcfg != -1:
            hmat[jcfg, icfg] += sign
    return hmat


def two_fermion(emat, lb, rb=None, tol=1E-10):

    if rb is None:
        rb = lb
    lb, rb = np.array(lb), np.array(rb)
    nr, nl, norbs = len(rb), len(lb), len(rb[0])
    indx = defaultdict(lambda: -1)
    for i, j in enumerate(lb):
        indx[tuple(j)] = i

    a1, a2 = np.nonzero(abs(emat) > tol)
    nonzero = np.stack((a1, a2), axis=-1)

    hmat = np.zeros((nl, nr), dtype=np.complex128)
    tmp_basis = np.zeros(norbs)
    for iorb, jorb in nonzero:
        for icfg in range(nr):
            tmp_basis[:] = rb[icfg]
            if tmp_basis[jorb] == 0:
                continue
            else:
                s1 = (-1)**np.count_nonzero(tmp_basis[0:jorb])
                tmp_basis[jorb] = 0
            if tmp_basis[iorb] == 1:
                continue
            else:
                s2 = (-1)**np.count_nonzero(tmp_basis[0:iorb])
                tmp_basis[iorb] = 1
            jcfg = indx[tuple(tmp_basis)]
            if jcfg != -1:
                hmat[jcfg, icfg] += emat[iorb, jorb] * s1 * s2
    return hmat


def four_fermion(umat, lb, rb=None, tol=1E-10):

    if rb is None:
        rb = lb
    lb, rb = np.array(lb), np.array(rb)
    nr, nl, norbs = len(rb), len(lb), len(rb[0])
    indx = defaultdict(lambda: -1)
    for i, j in enumerate(lb):
        indx[tuple(j)] = i

    a1, a2, a3, a4 = np.nonzero(abs(umat) > tol)
    nonzero = np.stack((a1, a2, a3, a4), axis=-1)

    hmat = np.zeros((nl, nr), dtype=np.complex128)
    tmp_basis = np.zeros(norbs)
    for lorb, korb, jorb, iorb in nonzero:
        if iorb == jorb or korb == lorb:
            continue
        for icfg in range(nr):
            tmp_basis[:] = rb[icfg]
            if tmp_basis[iorb] == 0:
                continue
            else:
                s1 = (-1)**np.count_nonzero(tmp_basis[0:iorb])
                tmp_basis[iorb] = 0
            if tmp_basis[jorb] == 0:
                continue
            else:
                s2 = (-1)**np.count_nonzero(tmp_basis[0:jorb])
                tmp_basis[jorb] = 0
            if tmp_basis[korb] == 1:
                continue
            else:
                s3 = (-1)**np.count_nonzero(tmp_basis[0:korb])
                tmp_basis[korb] = 1
            if tmp_basis[lorb] == 1:
                continue
            else:
                s4 = (-1)**np.count_nonzero(tmp_basis[0:lorb])
                tmp_basis[lorb] = 1
            jcfg = indx[tuple(tmp_basis)]
            if jcfg != -1:
                hmat[jcfg, icfg] += umat[lorb, korb, jorb, iorb] * s1 * s2 * s3 * s4
    return hmat


def build_opers(nfermion, coeff, lb, rb=None, tol=1E-10):

    if nfermion not in [2, 4]:
        raise Exception("nfermion is not 2 or 4")
    nl = len(lb)
    if rb is None:
        nr = nl
    else:
        nr = len(rb)
    coeff = np.array(coeff, order='C')
    if nfermion == 2:
        dim = coeff.shape
        if len(dim) < 2:
            raise Exception("Dimension of coeff should be at least 2 when nfermion=2")
        elif len(dim) == 2:
            hmat = two_fermion(coeff, lb, rb, tol)
        else:
            tot = np.prod(dim[0:-2])
            hmat_tmp = np.zeros((tot, nl, nr), dtype=np.complex)
            coeff_tmp = coeff.reshape((tot, dim[-2], dim[-1]))
            for i in range(tot):
                hmat_tmp[i] = two_fermion(coeff_tmp[i], lb, rb, tol)
            hmat = hmat_tmp.reshape(dim[0:-2] + (nl, nr))
    if nfermion == 4:
        dim = coeff.shape
        if len(dim) < 4:
            raise Exception("Dimension of coeff should be at least 4 when nfermion=4")
        elif len(dim) == 4:
            hmat = four_fermion(coeff, lb, rb, tol)
        else:
            tot = np.prod(dim[0:-4])
            hmat_tmp = np.zeros((tot, nl, nr), dtype=np.complex)
            coeff_tmp = coeff.reshape((tot, dim[-4], dim[-3], dim[-2], dim[-1]))
            for i in range(tot):
                hmat_tmp[i] = four_fermion(coeff_tmp[i], lb, rb, tol)
            hmat = hmat_tmp.reshape(dim[0:-4] + (nl, nr))

    return hmat


def density_matrix(iorb, jorb, lb, rb):

    lb, rb = np.array(lb), np.array(rb)
    nr, nl, norbs = len(rb), len(lb), len(rb[0])
    indx = defaultdict(lambda: -1)
    for i, j in enumerate(lb):
        indx[tuple(j)] = i

    hmat = np.zeros((nl, nr), dtype=np.complex128)
    tmp_basis = np.zeros(norbs)
    for icfg in range(nr):
        tmp_basis[:] = rb[icfg]
        if tmp_basis[jorb] == 0:
            continue
        else:
            s1 = (-1)**np.count_nonzero(tmp_basis[0:jorb])
            tmp_basis[jorb] = 0
        if tmp_basis[iorb] == 1:
            continue
        else:
            s2 = (-1)**np.count_nonzero(tmp_basis[0:iorb])
            tmp_basis[iorb] = 1
        jcfg = indx[tuple(tmp_basis)]
        if jcfg != -1:
            hmat[jcfg, icfg] += s1 * s2
    return hmat
