from enum import Enum


class HeatingStatus(Enum):
    MANUAL = 0
    CURVE = 1
    UART = 2


class OvenStatus:
    on: bool = False
    heating: bool = False

    p: float = 30.0
    i: float = 0.2
    d: float = 400.0

    reference_temp: float = 0.0
    internal_temp: float = 0.0

    heating_status: HeatingStatus = HeatingStatus.UART
