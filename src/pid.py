import os
import ctypes

pid_so = os.path.join(os.path.dirname(__file__), 'pid_c', 'pid.so')
module = ctypes.CDLL(pid_so)
module.pid_configura_constantes.argtypes = [ctypes.c_double] * 3
module.pid_atualiza_referencia.argtypes = [ctypes.c_float]
module.pid_controle.argtypes = [ctypes.c_double]
module.pid_controle.restype = ctypes.c_double


def config_constants(Kp: float, Ki: float, Kd: float) -> None:
    return module.pid_configura_constantes(Kp, Ki, Kd)


def update_reference(ref: float) -> None:
    return module.pid_atualiza_referencia(ref)


def control(output_mensure: float) -> float:
    return module.pid_controle(output_mensure)
