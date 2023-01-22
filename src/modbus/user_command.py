from enum import IntEnum


class UserCommand(IntEnum):
    NONE = 0x00
    OVEN_ON = 0xA1
    OVEN_OFF = 0xA2
    START_HEATING = 0xA3
    CANCEL = 0xA4
    TOGGLE_TEMP_MODE = 0xA5
