# python version 3.8

import re
# 基本数据，保存slater,soc这些
class AtomBasicData:
    def __init__(self,
                 v_name=None,
                 v_noccu=None,
                 c_name=None,
                 c_noccu=None,
                 slater_Fx_vv=None,
                 slater_Fx_vc=None,
                 slater_Gx_vc=None,
                 slater_Fx_cc=None,
                 v_soc=None,  # 只存initial
                 c_soc=None):
        self.v_name = v_name if v_name is not None else ""  # str
        self.v_noccu = v_noccu  # int
        self.c_name = c_name if c_name is not None else ""  # str
        self.c_noccu = c_noccu  # int
        self.slater_Fx_vv = slater_Fx_vv if slater_Fx_vv is not None else []  # list of float
        self.slater_Fx_vc = slater_Fx_vc if slater_Fx_vc is not None else []  # list of float
        self.slater_Gx_vc = slater_Gx_vc if slater_Gx_vc is not None else []  # list of float
        self.slater_Fx_cc = slater_Fx_cc if slater_Fx_cc is not None else []  # list of float
        self.v_soc = v_soc  # float-float
        self.c_soc = c_soc  # float

class DataManager_atom:
    def __init__(self):
        # 存放一组AtomBasicData，也就是放在列表里的实际数据，用v_name+v_noccu+'_'+c_name+c_noccu作为key
        self.atomBasicDataList = {}

    def getNameFromAtomData(atomData: AtomBasicData) -> str:
        if atomData.v_name is None or len(atomData.v_name) == 0:
            return ""
        name = atomData.v_name
        if atomData.v_noccu is not None:
            name = name + str(atomData.v_noccu)
        if len(atomData.c_name) > 0:
            name = name + "_" + atomData.c_name
            if atomData.c_noccu is not None:
                name = name + str(atomData.c_noccu)
        return name

    def addAtomData(self, atomData: AtomBasicData) -> bool:
        dictKey = DataManager_atom.getNameFromAtomData(atomData)
        if len(dictKey) == 0:
            return False
        self.atomBasicDataList[dictKey] = atomData  # 已经存在的话直接覆盖
        return True

    def getAtomDataByName(self, name: str) -> AtomBasicData or None:
        if name in self.atomBasicDataList.keys():
            return self.atomBasicDataList[name]
        else:
            return None

class SpectraBasicData:
    def __init__(self,
                 name=None,
                 poltype=None,
                 thin=None,
                 thout=None,
                 phi=None,
                 ominc=None,
                 eloss=None,
                 gamma_c=None,
                 gamma_f=None,
                 scattering_axis=None,
                 eval_i=None,
                 eval_n=None,
                 trans_op=None,
                 gs_list=None,
                 temperature=None,
                 spectra=None):
        self.name = name if name is not None else ""
        self.poltype = poltype if poltype is not None else ""  # (str,str)
        self.thin = thin  # float
        self.thout = thout if thout is not None else ""  # float
        self.phi = phi  # float
        self.ominc = ominc if ominc is not None else []  # list of float
        self.eloss = eloss if eloss is not None else []  # list of float
        self.gamma_c = gamma_c if gamma_c is not None else []  # list of float
        self.gamma_f = gamma_f if gamma_f is not None else []  # list of float
        self.scattering_axis = scattering_axis if scattering_axis is not None else [[]]  # list of list
        self.eval_i = eval_i if eval_i is not None else []  # list of list
        self.eval_n = eval_n if eval_n is not None else []  # list of list
        self.trans_op = trans_op if trans_op is not None else [[]]  # list of list
        self.gs_list = gs_list if gs_list is not None else []  # list
        self.temperature = temperature if temperature is not None else "" # float
        self.spectra = spectra if spectra is not None else "{}"

class DataManager_spectra:
    def __init__(self):
        # 存放一组AtomBasicData，也就是放在列表里的实际数据，用v_name+v_noccu+'_'+c_name+c_noccu作为key
        self.spectraBasicDataList = {}
        self.currentSpectraBasicData = {}  # 到时候用来存放正要处理的数据

    def getNameFromSpectraData(spectraData: SpectraBasicData) -> str:
        if spectraData.name is None or len(spectraData.name) == 0:
            return ""
        return spectraData.name

    def addSpectraData(self, spectraData: SpectraBasicData) -> bool:
        dictKey = DataManager_spectra.getNameFromSpectraData(spectraData)
        if len(dictKey) == 0:
            return False
        self.spectraBasicDataList[dictKey] = spectraData  # 已经存在的话直接覆盖
        return True

    def getSpectraDataByName(self, name: str) -> SpectraBasicData or None:
        if name in self.spectraBasicDataList.keys():
            return self.spectraBasicDataList[name]
        else:
            return None


if __name__ == "__main__":
    pass
