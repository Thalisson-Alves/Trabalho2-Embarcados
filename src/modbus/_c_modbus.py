import ctypes
import os
from enum import Enum
from types import DynamicClassAttribute
from typing import Union
import logging

from utils.settings import SO_DIR
from utils import exceptions

modbus_so = os.path.join(SO_DIR, 'modbus.so')
module = ctypes.CDLL(modbus_so, use_errno=True)
module.uart_send.argtypes = [ctypes.c_ubyte, ctypes.c_int, ctypes.c_void_p,
                             ctypes.c_uint, ctypes.c_void_p]
module.uart_send.restype = ctypes.c_int

c2py = {int: ctypes.c_int, float: ctypes.c_float, bool: ctypes.c_byte}


class _RequestCommand(Enum):
    INTERNAL_TEMP = (0xc1, ctypes.c_float, 9)
    REFERENCE_TEMP = (0xc2, ctypes.c_float, 9)
    REQUEST_COMMAND = (0xc3, ctypes.c_int, 9)
    SEND_INT = (0xd1, type(None), 5)
    SEND_FLOAT = (0xd2, type(None), 5)
    SEND_SYS_STATE = (0xd3, ctypes.c_int, 9)
    SEND_CONTROL_MODE = (0xd4, ctypes.c_int, 9)
    SEND_FUNC_STATE = (0xd5, ctypes.c_int, 9)
    SEND_AMB_TEMPO = (0xd6, ctypes.c_float, 9)

    @DynamicClassAttribute
    def code(self):
        return self._value_[0]

    @DynamicClassAttribute
    def return_type(self):
        return self._value_[1]

    @DynamicClassAttribute
    def res_size(self):
        return self._value_[2]


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
    err = module.uart_send(command.code, command.res_size, value, size, out if out is None else ctypes.byref(out))

    errno = ctypes.get_errno()
    logging.getLogger('debug').info(f'Called with {command.name}. Got {err} - :{errno}:{os.strerror(errno)}:')

    if err == 1:
        raise exceptions.ModbusWriteError('Failed to write value to uart')
    elif err == 2:
        raise exceptions.ModbusReadError('Failed to read value from uart')
    elif err == 3:
        raise exceptions.ModbusCRCError('CRC Missmatch')

    return out.value if out else None
