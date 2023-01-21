import ctypes
import os
from enum import Enum
from types import DynamicClassAttribute
from typing import Union

from utils.settings import SO_DIR

modbus_so = os.path.join(SO_DIR, 'modbus.so')
module = ctypes.CDLL(modbus_so)
module.uart_send.argtypes = [ctypes.c_ubyte, ctypes.c_void_p,
                             ctypes.c_uint, ctypes.c_void_p]
module.uart_send.restype = ctypes.c_int

c2py = {int: ctypes.c_int, float: ctypes.c_float, bool: ctypes.c_byte}


class _RequestCommand(Enum):
    INTERNAL_TEMP = (0xc1, ctypes.c_float)
    REFERENCE_TEMP = (0xc2, ctypes.c_float)
    REQUEST_COMMAND = (0xc3, ctypes.c_int)
    SEND_INT = (0xd1, type(None))
    SEND_FLOAT = (0xd2, type(None))
    SEND_SYS_STATE = (0xd3, ctypes.c_int)
    SEND_CONTROL_MODE = (0xd4, ctypes.c_int)
    SEND_FUNC_STATE = (0xd5, ctypes.c_int)
    SEND_AMB_TEMPO = (0xd6, ctypes.c_float)

    @DynamicClassAttribute
    def code(self):
        return self._value_[0]

    @DynamicClassAttribute
    def return_type(self):
        return self._value_[1]


def init() -> None:
    return module.uart_init()


def close() -> None:
    return module.uart_close()


def send(command: _RequestCommand, value: Union[int, float, bool, None] = None) -> Union[int, float, None]:
    size = 0
    if value is not None:
        c_type = c2py[type(value)]
        size = ctypes.sizeof(c_type)
        value = ctypes.byref(c_type(value))  # type: ignore

    out = command.return_type()
    if module.uart_send(command.code, value, size,
                        out if out is None else ctypes.byref(out)):
        raise RuntimeError('Error on uart_send')

    return out if out is None else out.value
