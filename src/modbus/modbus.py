from ._c_modbus import _init, _send, _RequestCommand

from utils.singleton import SingletonMeta


class Modbus(metaclass=SingletonMeta):
    def __init__(self) -> None:
        _init()

    @property
    def internal_temp(self) -> float:
        return _send(_RequestCommand.INTERNAL_TEMP)  # type: ignore

    @property
    def reference_temp(self) -> float:
        return _send(_RequestCommand.REFERENCE_TEMP)  # type: ignore

    @property
    def read_command(self) -> int:
        return _send(_RequestCommand.REQUEST_COMMAND)  # type: ignore

    def send_control_sign(self, value: int) -> None:
        _send(_RequestCommand.SEND_INT, value)

    def send_reference_temp(self, value: float) -> None:
        _send(_RequestCommand.SEND_FLOAT, value)

    def send_system_status(self, status: bool) -> int:
        return _send(_RequestCommand.SEND_SYS_STATE, status)  # type: ignore

    def send_control_status(self, status: bool) -> int:
        return _send(_RequestCommand.SEND_CONTROL_MODE, status)  # type: ignore

    def send_working_status(self, status: bool) -> int:
        return _send(_RequestCommand.SEND_FUNC_STATE, status)  # type: ignore

    def send_room_temp(self, value: float) -> float:
        return _send(_RequestCommand.SEND_AMB_TEMPO, value)  # type: ignore
