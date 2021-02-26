__all__ = ['write_tensor', 'write_emat', 'write_umat', 'write_config',
           'read_poles_from_file', 'dump_poles', 'load_poles']

import numpy as np
import json


def write_tensor_1(tensor, fname, only_nonzeros=False, tol=1E-10, fmt_int='{:10d}',
                   fmt_float='{:.15f}'):
    (n1, ) = tensor.shape
    is_cmplx = False
    if tensor.dtype == np.complex or tensor.dtype == np.complex128:
        is_cmplx = True
    space = "    "
    f = open(fname, 'w')
    for i in range(n1):
        if only_nonzeros and abs(tensor[i]) < tol:
            continue
        if is_cmplx:
            fmt_string = fmt_int + space + (fmt_float + space) * 2 + '\n'
            f.write(fmt_string.format(i + 1, tensor[i].real, tensor[i].imag))
        else:
            fmt_string = fmt_int + space + fmt_float + space + '\n'
            f.write(fmt_string.format(i + 1, tensor[i]))
    f.close()


def write_tensor_2(tensor, fname, only_nonzeros=False, tol=1E-10, fmt_int='{:10d}',
                   fmt_float='{:.15f}'):
    (n1, n2) = tensor.shape
    is_cmplx = False
    if tensor.dtype == np.complex or tensor.dtype == np.complex128:
        is_cmplx = True
    space = "    "
    f = open(fname, 'w')
    for i in range(n1):
        for j in range(n2):
            if only_nonzeros and abs(tensor[i, j]) < tol:
                continue
            if is_cmplx:
                fmt_string = (fmt_int + space) * 2 + (fmt_float + space) * 2 + '\n'
                f.write(fmt_string.format(i + 1, j + 1, tensor[i, j].real, tensor[i, j].imag))
            else:
                fmt_string = (fmt_int + space) * 2 + fmt_float + space + '\n'
                f.write(fmt_string.format(i + 1, j + 1, tensor[i, j]))
    f.close()


def write_tensor_3(tensor, fname, only_nonzeros=False, tol=1E-10, fmt_int='{:10d}',
                   fmt_float='{:.15f}'):
    (n1, n2, n3) = tensor.shape
    is_cmplx = False
    if tensor.dtype == np.complex or tensor.dtype == np.complex128:
        is_cmplx = True
    space = "    "
    f = open(fname, 'w')
    for i in range(n1):
        for j in range(n2):
            for k in range(n3):
                if only_nonzeros and abs(tensor[i, j, k]) < tol:
                    continue
                if is_cmplx:
                    fmt_string = (fmt_int + space) * 3 + (fmt_float + space) * 2 + '\n'
                    f.write(fmt_string.format(i + 1, j + 1, k + 1, tensor[i, j, k].real,
                                              tensor[i, j, k].imag))
                else:
                    fmt_string = (fmt_int + space) * 3 + fmt_float + space + '\n'
                    f.write(fmt_string.format(i + 1, j + 1, k + 1, tensor[i, j, k]))
    f.close()


def write_tensor_4(tensor, fname, only_nonzeros=False, tol=1E-10, fmt_int='{:10d}',
                   fmt_float='{:.15f}'):
    (n1, n2, n3, n4) = tensor.shape
    is_cmplx = False
    if tensor.dtype == np.complex or tensor.dtype == np.complex128:
        is_cmplx = True
    space = "    "
    f = open(fname, 'w')
    for i in range(n1):
        for j in range(n2):
            for k in range(n3):
                for m in range(n4):
                    if only_nonzeros and abs(tensor[i, j, k, m]) < tol:
                        continue
                    if is_cmplx:
                        fmt_string = (fmt_int + space) * 4 + (fmt_float + space) * 2 + '\n'
                        f.write(fmt_string.format(i + 1, j + 1, k + 1, m + 1,
                                tensor[i, j, k, m].real, tensor[i, j, k, m].imag))
                    else:
                        fmt_string = (fmt_int + space) * 4 + fmt_float + space + '\n'
                        f.write(fmt_string.format(i + 1, j + 1, k + 1, m + 1, tensor[i, j, k, m]))
    f.close()


def write_tensor_5(tensor, fname, only_nonzeros=False, tol=1E-10, fmt_int='{:10d}',
                   fmt_float='{:.15f}'):
    (n1, n2, n3, n4, n5) = tensor.shape
    is_cmplx = False
    if tensor.dtype == np.complex or tensor.dtype == np.complex128:
        is_cmplx = True
    space = "    "
    f = open(fname, 'w')
    for i in range(n1):
        for j in range(n2):
            for k in range(n3):
                for r in range(n4):
                    for m in range(n5):
                        if only_nonzeros and abs(tensor[i, j, k, r, m]) < tol:
                            continue
                        if is_cmplx:
                            fmt_string = (fmt_int + space) * 5 + (fmt_float + space) * 2 + '\n'
                            f.write(fmt_string.format(i + 1, j + 1, k + 1, r + 1, m + 1,
                                    tensor[i, j, k, r, m].real, tensor[i, j, k, r, m].imag))
                        else:
                            fmt_string = (fmt_int + space) * 5 + fmt_float + space + '\n'
                            f.write(fmt_string.format(i + 1, j + 1, k + 1, r + 1, m + 1,
                                    tensor[i, j, k, r, m]))
    f.close()


def write_tensor(tensor, fname, only_nonzeros=False, tol=1E-10, fmt_int='{:10d}',
                 fmt_float='{:.15f}'):

    ndim = tensor.ndim
    if ndim == 1:
        write_tensor_1(tensor, fname, only_nonzeros=only_nonzeros, tol=tol,
                       fmt_int=fmt_int, fmt_float=fmt_float)
    elif ndim == 2:
        write_tensor_2(tensor, fname, only_nonzeros=only_nonzeros, tol=tol,
                       fmt_int=fmt_int, fmt_float=fmt_float)
    elif ndim == 3:
        write_tensor_3(tensor, fname, only_nonzeros=only_nonzeros, tol=tol,
                       fmt_int=fmt_int, fmt_float=fmt_float)
    elif ndim == 4:
        write_tensor_4(tensor, fname, only_nonzeros=only_nonzeros, tol=tol,
                       fmt_int=fmt_int, fmt_float=fmt_float)
    elif ndim == 5:
        write_tensor_5(tensor, fname, only_nonzeros=only_nonzeros, tol=tol,
                       fmt_int=fmt_int, fmt_float=fmt_float)
    else:
        raise Exception("error in write_tensor: ndim >5, not implemented !")


def write_emat(emat, fname, tol=1E-12, fmt_int='{:10d}', fmt_float='{:.15f}'):

    a1, a2 = np.nonzero(abs(emat) > tol)
    nonzero = np.stack((a1, a2), axis=-1)

    space = "    "
    fmt_string = (fmt_int + space) * 2 + (fmt_float + space) * 2 + '\n'
    f = open(fname, 'w')
    if len(nonzero) == 0:
        f.write("{:10d}\n".format(1))
        f.write(fmt_string.format(1, 1, 0.0, 0.0))
    else:
        f.write("{:20d}\n".format(len(nonzero)))
        for i, j in nonzero:
            f.write(fmt_string.format(i + 1, j + 1, emat[i, j].real, emat[i, j].imag))
    f.close()


def write_umat(umat, fname, tol=1E-12, fmt_int='{:10d}', fmt_float='{:.15f}'):

    a1, a2, a3, a4 = np.nonzero(abs(umat) > tol)
    nonzero = np.stack((a1, a2, a3, a4), axis=-1)

    space = "    "
    fmt_string = (fmt_int + space) * 4 + (fmt_float + space) * 2 + '\n'
    f = open(fname, 'w')
    if len(nonzero) == 0:
        f.write("{:10d}\n".format(1))
        f.write(fmt_string.format(1, 1, 1, 1, 0.0, 0.0))
    else:
        f.write("{:20d}\n".format(len(nonzero)))
        for i, j, k, l in nonzero:
            f.write(fmt_string.format(i + 1, j + 1, k + 1, l + 1,
                                      umat[i, j, k, l].real, umat[i, j, k, l].imag))
    f.close()


def write_config(
        directory='.', ed_solver=1, num_val_orbs=2, num_core_orbs=2,
        neval=1, nvector=1, ncv=1, idump=True, num_gs=1, maxiter=500,
        linsys_max=1000, min_ndim=1000, nkryl=500, eigval_tol=1e-8,
        linsys_tol=1e-10, omega_in=0.0, gamma_in=0.1
        ):

    if idump:
        dump_vector = '.true.'
    else:
        dump_vector = '.false.'

    config = [
        "&control",
        "ed_solver=" + str(ed_solver),
        "num_val_orbs=" + str(num_val_orbs),
        "num_core_orbs=" + str(num_core_orbs),
        "neval=" + str(neval),
        "nvector=" + str(nvector),
        "ncv=" + str(ncv),
        "idump=" + str(dump_vector),
        "num_gs=" + str(num_gs),
        "maxiter=" + str(maxiter),
        "linsys_max=" + str(linsys_max),
        "min_ndim=" + str(min_ndim),
        "nkryl=" + str(nkryl),
        "eigval_tol=" + str(eigval_tol),
        "linsys_tol=" + str(linsys_tol),
        "omega_in=" + str(omega_in),
        "gamma_in=" + str(gamma_in),
        "&end"
    ]

    f = open(directory + '/config.in', 'w')
    for item in config:
        f.write(item + "\n")
    f.close()


def read_poles_from_file(file_list):

    pole_dict = {
        'npoles': [],
        'eigval': [],
        'norm': [],
        'alpha': [],
        'beta': []
    }
    for fname in file_list:
        f = open(fname, 'r')
        line = f.readline()
        neff = int(line.strip().split()[1])
        pole_dict['npoles'].append(neff)

        line = f.readline()
        eigval = float(line.strip().split()[1])
        pole_dict['eigval'].append(eigval)

        line = f.readline()
        norm = float(line.strip().split()[1])
        pole_dict['norm'].append(norm)

        alpha = []
        beta = []
        for i in range(neff):
            line = f.readline()
            line = line.strip().split()
            alpha.append(float(line[1]))
            beta.append(float(line[2]))
        pole_dict['alpha'].append(alpha)
        pole_dict['beta'].append(beta)
        f.close()

    return pole_dict


def dump_poles(obj, file_name="poles"):

    with open(file_name+'.json', 'w') as f:
        json.dump(obj, f, indent=2)


def load_poles(file_name='poles'):

    with open(file_name+'.json', 'r') as f:
        obj = json.load(f)

    return obj
