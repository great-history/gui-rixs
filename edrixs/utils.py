__all__ = ['beta_to_kelvin', 'kelvin_to_beta', 'boltz_dist', 'UJ_to_UdJH',
           'UdJH_to_UJ', 'UdJH_to_F0F2F4', 'UdJH_to_F0F2F4F6', 'F0F2F4_to_UdJH',
           'F0F2F4_to_UJ', 'F0F2F4F6_to_UdJH', 'CT_imp_bath',
           'CT_imp_bath_core_hole', 'info_atomic_shell',
           'case_to_shell_name', 'edge_to_shell_name', 'slater_integrals_name',
           'get_atom_data', 'rescale']

import numpy as np
import json
import pkg_resources


def beta_to_kelvin(beta):

    kb = 8.6173303E-5
    ev = 1.0 / float(beta)
    T = ev / kb
    return T


def kelvin_to_beta(k):

    kb = 8.6173303E-5
    beta = 1.0 / (kb * k)
    return beta


def boltz_dist(gs, T):

    tmp_gs = np.array(gs)
    beta = kelvin_to_beta(T)
    res = np.exp(-beta * (tmp_gs - min(tmp_gs))) / np.sum(np.exp(-beta * (tmp_gs - min(tmp_gs))))
    return res


def UJ_to_UdJH(U, J):

    F2 = J / (3.0 / 49.0 + 20 * 0.625 / 441.0)
    F4 = 0.625 * F2
    JH = (F2 + F4) / 14.0
    Ud = U - 4.0 / 49.0 * (F2 + F4)

    return Ud, JH


def UdJH_to_UJ(Ud, JH):

    F2 = 14.0 / 1.625 * JH
    F4 = 0.625 * F2
    J = 3.0 / 49.0 * F2 + 20 / 441.0 * F4
    U = Ud + 4.0 / 49.0 * (F2 + F4)

    return U, J


def UdJH_to_F0F2F4(Ud, JH):

    F0 = Ud
    F2 = 14 / 1.625 * JH
    F4 = 0.625 * F2

    return F0, F2, F4


def UdJH_to_F0F2F4F6(Ud, JH):

    F0 = Ud
    F2 = 6435 / (286.0 + (195 * 451) / 675.0 + (250 * 1001) / 2025.0) * JH
    F4 = 451 / 675.0 * F2
    F6 = 1001 / 2025.0 * F2

    return F0, F2, F4, F6


def F0F2F4_to_UdJH(F0, F2, F4):

    Ud = F0
    JH = (F2 + F4) / 14.0

    return Ud, JH


def F0F2F4_to_UJ(F0, F2, F4):

    U = F0 + 4.0 / 49.0 * (F2 + F4)
    J = 3.0 / 49.0 * F2 + 20 / 441.0 * F4

    return U, J


def F0F2F4F6_to_UdJH(F0, F2, F4, F6):

    Ud = F0
    JH = (286 * F2 + 195 * F4 + 250 * F6) / 6435.0
    return Ud, JH


def CT_imp_bath(U_dd, Delta, n):

    E_d = (10*Delta - n*(19 + n)*U_dd/2)/(10 + n)
    E_L = n*((1 + n)*U_dd/2-Delta)/(10 + n)
    return E_d, E_L


def CT_imp_bath_core_hole(U_dd, U_pd, Delta, n):

    E_dc = (10*Delta - n*(31 + n)*U_dd/2 - 90*U_pd) / (16 + n)
    E_Lc = ((1 + n)*(n*U_dd/2 + 6*U_pd) - (6 + n)*Delta) / (16 + n)
    E_p = (10*Delta + (1 + n)*(n*U_dd/2 - (10 + n)*U_pd)) / (16 + n)
    return E_dc, E_Lc, E_p


def info_atomic_shell():

    info = {'s':   (0, 2),
            'p':   (1, 6),
            'p12': (1, 2),
            'p32': (1, 4),
            't2g': (2, 6),
            'd':   (2, 10),
            'd32': (2, 4),
            'd52': (2, 6),
            'f':   (3, 14),
            'f52': (3, 6),
            'f72': (3, 8)
            }

    return info


def case_to_shell_name(case):

    shell = ['s', 'p', 'p12', 'p32', 't2g', 'd', 'd32', 'd52', 'f', 'f52', 'f72']

    shell_name = {}
    for str1 in shell:
        shell_name[str1] = (str1,)

    for str1 in shell:
        for str2 in shell:
            shell_name[str1+str2] = (str1, str2)

    return shell_name[case.strip()]


def edge_to_shell_name(edge_name, with_main_qn=False):

    shell_name = {
        'K': ('s', '1s'),
        'L1': ('s', '2s'),
        'L2': ('p12', '2p12'),
        'L3': ('p32', '2p32'),
        'L23': ('p', '2p'),
        'M1': ('s', '3s'),
        'M2': ('p12', '3p12'),
        'M3': ('p32', '3p32'),
        'M23': ('p', '3p'),
        'M4': ('d32', '3d32'),
        'M5': ('d52', '3d52'),
        'M45': ('d', '3d'),
        'N1': ('s', '4s'),
        'N2': ('p12', '4p12'),
        'N3': ('p32', '4p32'),
        'N23': ('p', '4p'),
        'N4': ('d32', '4d32'),
        'N5': ('d52', '4d52'),
        'N45': ('d', '4d'),
        'N6': ('f52', '4f52'),
        'N7': ('f72', '4f72'),
        'N67': ('f', '4f'),
        'O1': ('s', '5s'),
        'O2': ('p12', '5p12'),
        'O3': ('p32', '5p32'),
        'O23': ('p', '5p'),
        'O4': ('d32', '5d32'),
        'O5': ('d52', '5d52'),
        'O45': ('d', '5d'),
        'P1': ('s', '6s'),
        'P2': ('p12', '6p12'),
        'P3': ('p32', '6p32'),
        'P23': ('p', '6p')
    }

    if with_main_qn:
        return shell_name[edge_name.strip()][1]
    else:
        return shell_name[edge_name.strip()][0]


def slater_integrals_name(shell_name, label=None):

    info = info_atomic_shell()
    # one shell
    if len(shell_name) == 1:
        res = []
        l1 = info[shell_name[0]][0]
        if label is not None:
            x = label[0]
        else:
            x = '1'
        res.extend(['F' + str(i) + '_' + x + x for i in range(0, 2*l1+1, 2)])
    elif len(shell_name) == 2:
        res = []
        l1 = info[shell_name[0]][0]
        l2 = info[shell_name[1]][0]
        if label is not None:
            x, y = label[0], label[1]
        else:
            x, y = '1', '2'
        res.extend(['F' + str(i) + '_' + x + x for i in range(0, 2*l1+1, 2)])
        res.extend(['F' + str(i) + '_' + x + y for i in range(0, min(2*l1, 2*l2)+1, 2)])
        res.extend(['G' + str(i) + '_' + x + y for i in range(abs(l1-l2), l1+l2+1, 2)])
        res.extend(['F' + str(i) + '_' + y + y for i in range(0, 2*l2+1, 2)])
    elif len(shell_name) == 3:
        res = []
        l1 = info[shell_name[0]][0]
        l2 = info[shell_name[1]][0]
        l3 = info[shell_name[2]][0]
        if label is not None:
            x, y, z = label[0], label[1], label[2]
        else:
            x, y, z = '1', '2', '3'
        res.extend(['F' + str(i) + '_' + x + x for i in range(0, 2*l1+1, 2)])
        res.extend(['F' + str(i) + '_' + x + y for i in range(0, min(2*l1, 2*l2)+1, 2)])
        res.extend(['G' + str(i) + '_' + x + y for i in range(abs(l1-l2), l1+l2+1, 2)])
        res.extend(['F' + str(i) + '_' + y + y for i in range(0, 2*l2+1, 2)])
        res.extend(['F' + str(i) + '_' + x + z for i in range(0, min(2*l1, 2*l3)+1, 2)])
        res.extend(['G' + str(i) + '_' + x + z for i in range(abs(l1-l3), l1+l3+1, 2)])
        res.extend(['F' + str(i) + '_' + y + z for i in range(0, min(2*l2, 2*l3)+1, 2)])
        res.extend(['G' + str(i) + '_' + y + z for i in range(abs(l2-l3), l2+l3+1, 2)])
        res.extend(['F' + str(i) + '_' + z + z for i in range(0, 2*l3+1, 2)])
    else:
        raise Exception("Not implemented for this case: ", shell_name)

    return res


def get_atom_data(atom, v_name, v_noccu, edge=None, trans_to_which=1, label=None):

    c_norb = {'s': 2, 'p': 6, 'd': 10, 'f': 14}
    atom = atom.strip()
    avail_atoms = ['Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu',
                   'Re', 'Os', 'Ir',
                   'Sm',
                   'U', 'Pu']
    avail_shells = ['1s', '2s', '2p', '3s', '3p', '3d', '4s', '4p', '4d', '4f',
                    '5s', '5p', '5d', '5f', '6s', '6p', '6d']

    if atom not in avail_atoms:
        raise Exception("Atom data is Not available for this atom: ", atom)

    if not isinstance(v_name, (list, tuple)):
        v_name = (v_name,)
    if not isinstance(v_noccu, (list, tuple)):
        v_noccu = (v_noccu,)

    if label is not None:
        if not isinstance(label, (list, tuple)):
            label = (label,)

    if len(v_name) != len(v_noccu):
        raise Exception("The shape of v_name is not same as noccu")

    for ishell in v_name:
        if ishell not in avail_shells:
            raise Exception("Not available for this shell: ", ishell)

    fname = pkg_resources.resource_filename('edrixs', 'atom_data/'+atom+'.json')
    with open(fname, 'r') as f:
        atom_dict = json.load(f)

    res = {}
    shell_name = []
    for name in v_name:
        shell_name.append(name[-1])
    if label is not None:
        my_label = label[0:len(shell_name)]
    else:
        my_label = None
    slater_name = slater_integrals_name(shell_name, label=my_label)

    if len(v_name) == 1:
        case = v_name[0] + str(v_noccu[0])
    else:
        case = v_name[0] + str(v_noccu[0]) + '_' + v_name[1] + str(v_noccu[1])
    if case not in atom_dict:
        raise Exception("This configuration is not available in atom_data", case)

    nslat = len(slater_name)
    slater_i = [0.0] * nslat
    tmp = atom_dict[case]['slater']
    slater_i[0:len(tmp)] = tmp
    res['slater_i'] = list(zip(slater_name, slater_i))
    res['v_soc_i'] = atom_dict[case]['soc']

    if edge is not None:
        edge = edge.strip()
        edge_name = edge_to_shell_name(edge, with_main_qn=True)
        shell_name = []
        for name in v_name:
            shell_name.append(name[-1])
        shell_name.append(edge_name[1:2])
        if label is not None:
            my_label = label[0:len(shell_name)]
        else:
            my_label = None
        slater_name = slater_integrals_name(shell_name, label=my_label)

        if len(v_name) == 1:
            case = (v_name[0] + str(v_noccu[0]+1) + '_' +
                    edge_name[0:2] + str(c_norb[edge_name[1]]-1))
        else:
            if trans_to_which == 1:
                case = (v_name[0] + str(v_noccu[0]+1) + '_' +
                        v_name[1] + str(v_noccu[1]) + '_' +
                        edge_name[0:2] + str(c_norb[edge_name[1]]-1))
            else:
                case = (v_name[0] + str(v_noccu[0]) + '_' +
                        v_name[1] + str(v_noccu[1]+1) + '_' +
                        edge_name[0:2] + str(c_norb[edge_name[1]]-1))
        if case not in atom_dict:
            raise Exception("This configuration is currently not available in atom_data", case)

        nslat = len(slater_name)
        slater_n = [0.0] * nslat
        tmp = atom_dict[case]['slater']
        slater_n[0:len(tmp)] = tmp
        res['slater_n'] = list(zip(slater_name, slater_n))

        res['v_soc_n'] = atom_dict[case]['soc'][0:-1]
        res['c_soc'] = atom_dict[case]['soc'][-1]

        res['edge_ene'] = atom_dict[edge]['ene']
        res['gamma_c'] = [i / 2 for i in atom_dict[edge]['gamma']]

    return res


def rescale(old_list, scale=None):

    new_list = [i for i in old_list]
    if scale is not None:
        for pos, val in zip(scale[0], scale[1]):
            new_list[pos] = new_list[pos] * val
    return new_list
