from enum import Enum


class HeatingStatus(Enum):
    DEBUG = 0
    CURVE = 1
    DASHBOARD = 2


class OvenState:
    on: bool = False
    heating: bool = False
    heating_status: HeatingStatus = HeatingStatus.DASHBOARD

    p: float = 30.0
    i: float = 0.2
    d: float = 400.0

    reference_temp: float = 0.0
    internal_temp: float = 0.0
    room_temp: float = 0.0

    intensity: int = 0

