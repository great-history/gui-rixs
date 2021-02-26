#!/usr/bin/env python

__all__ = ['combination', 'fock_bin', 'get_fock_bin_by_N', 'get_fock_half_N',
           'get_fock_full_N', 'get_fock_basis_by_NLz', 'get_fock_basis_by_NSz',
           'get_fock_basis_by_NJz', 'get_fock_basis_by_N_abelian',
           'get_fock_basis_by_N_LzSz', 'write_fock_dec_by_N']

import numpy as np
import itertools


def combination(n, m):

    if m > n or n < 0 or m < 0:
        print("wrong number in combination")
        return
    if m == 0 or n == m:
        return 1

    largest = max(m, n - m)
    smallest = min(m, n - m)
    numer = 1.0
    for i in range(largest + 1, n + 1):
        numer *= i

    denom = 1.0
    for i in range(1, smallest + 1):
        denom *= i

    res = int(numer / denom)
    return res


def fock_bin(n, k):

    if n == 0:
        return [[0]]

    res = []
    for bits in itertools.combinations(list(range(n)), k):
        s = [0] * n
        for bit in bits:
            s[bit] = 1
        res.append(s)
    return res


def get_fock_bin_by_N(*args):

    n = len(args)

    if n % 2 != 0:
        print("Error: number of arguments is not even")
        return

    if n == 2:
        return fock_bin(args[0], args[1])
    else:
        result = []
        res1 = fock_bin(args[0], args[1])
        res2 = get_fock_bin_by_N(*args[2:])
        for ifock in res2:
            for jfock in res1:
                result.append(jfock + ifock)
        return result


def get_fock_half_N(N):
    res = [[] for i in range(N + 1)]
    for i in range(2**N):
        occu = bin(i).count('1')
        res[occu].append(i)
    return res


def get_fock_full_N(norb, N):

    res = []
    half_N = get_fock_half_N(norb // 2)
    for m in range(norb // 2 + 1):
        n = N - m
        if n >= 0 and n <= norb // 2:
            res.extend([i * 2**(norb // 2) + j for i in half_N[m] for j in half_N[n]])
    return res


def get_fock_basis_by_NLz(norb, N, lz_list):

    res = get_fock_basis_by_N_abelian(norb, N, lz_list)
    return res


def get_fock_basis_by_NSz(norb, N, sz_list):

    res = get_fock_basis_by_N_abelian(norb, N, sz_list)
    return res


def get_fock_basis_by_NJz(norb, N, jz_list):

    res = get_fock_basis_by_N_abelian(norb, N, jz_list)
    return res


def get_fock_basis_by_N_abelian(norb, N, a_list):

    result = get_fock_full_N(norb, N)
    min_a, max_a = min(a_list) * N, max(a_list) * N
    basis = {}
    for i in range(min_a, max_a + 1):
        basis[i] = []
    for n in result:
        a = sum([a_list[i] for i in range(0, n.bit_length()) if (n >> i & 1)])
        basis[a].append(n)
    return basis


def get_fock_basis_by_N_LzSz(norb, N, lz_list, sz_list):

    result = get_fock_full_N(norb, N)
    min_Lz, max_Lz = min(lz_list) * N, max(lz_list) * N
    min_Sz, max_Sz = min(sz_list) * N, max(sz_list) * N
    basis = {}
    for i in range(min_Lz, max_Lz + 1):
        for j in range(min_Sz, max_Sz + 1):
            basis[(i, j)] = []
    for n in result:
        Lz, Sz = np.sum([[lz_list[i], sz_list[i]] for i in range(0, n.bit_length())
                         if (n >> i & 1)], axis=0)
        basis[(Lz, Sz)].append(n)
    return basis


def write_fock_dec_by_N(N, r, fname='fock_i.in'):

    res = get_fock_full_N(N, r)
    res.sort()
    ndim = len(res)
    f = open(fname, 'w')
    print(ndim, file=f)
    for item in res:
        print(item, file=f)
    f.close()
    return ndim
