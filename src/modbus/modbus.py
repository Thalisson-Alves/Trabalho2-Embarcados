from ._c_modbus import _RequestCommand, send
from .user_command import UserCommand

from utils.exceptions import retry_log


@retry_log
def internal_temp() -> float:
    return send(_RequestCommand.INTERNAL_TEMP)  # type: ignore

@retry_log
def reference_temp() -> float:
    return send(_RequestCommand.REFERENCE_TEMP)  # type: ignore

@retry_log
def read_command() -> UserCommand:
    return UserCommand(send(_RequestCommand.REQUEST_COMMAND))

@retry_log
def send_control_signal(value: int) -> None:
    send(_RequestCommand.SEND_INT, value)

@retry_log
def send_reference_temp(value: float) -> None:
    send(_RequestCommand.SEND_FLOAT, value)

@retry_log
def send_system_status(status: bool) -> int:
    return send(_RequestCommand.SEND_SYS_STATE, status)  # type: ignore

@retry_log
def send_control_status(status: bool) -> int:
    return send(_RequestCommand.SEND_CONTROL_MODE, status)  # type: ignore

@retry_log
def send_working_status(status: bool) -> int:
    return send(_RequestCommand.SEND_FUNC_STATE, status)  # type: ignore

@retry_log
def send_room_temp(value: float) -> float:
    return send(_RequestCommand.SEND_AMB_TEMPO, value)  # type: ignore


__all__ = ('internal_temp', 'reference_temp', 'read_command', 'send_control_signal',
           'send_reference_temp', 'send_system_status', 'send_control_status', 
           'send_working_status', 'send_room_temp')
