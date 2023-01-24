import ctypes
import os
from typing import Union

from utils.settings import SO_DIR

pid_so = os.path.join(SO_DIR, 'pid.so')
module = ctypes.CDLL(pid_so)
module.pid_configura_constantes.argtypes = [ctypes.c_double] * 3
module.pid_atualiza_referencia.argtypes = [ctypes.c_double]
module.pid_controle.argtypes = [ctypes.c_double]
module.pid_controle.restype = ctypes.c_double


def config_constants(Kp: float, Ki: float, Kd: float) -> None:
    return module.pid_configura_constantes(Kp, Ki, Kd)


def update_reference(ref: float) -> None:
    return module.pid_atualiza_referencia(ref)


def control(output_mensure: Union[float, int]) -> float:
    return module.pid_controle(float(output_mensure))
