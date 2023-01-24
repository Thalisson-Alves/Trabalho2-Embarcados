import time
import modbus
import gpio
import i2c
import pid
from oven_status import OvenState, HeatingStatus
from utils import settings
import logging
import threading


def handle_user_command():
    logger = logging.getLogger('debug')
    while True:
        time.sleep(2)
        command = modbus.read_command()
        logger.debug(f'Got command {command}')

        if command is None: continue

        if command == command.OVEN_ON:
            logger.debug(f'On OVEN_ON')
            OvenState.on = True
            modbus.send_system_status(OvenState.on)
        elif command == command.OVEN_OFF:
            logger.debug(f'On OVEN_OFF')
            OvenState.on = False
            OvenState.heating = False
            modbus.send_system_status(OvenState.on)
            modbus.send_working_status(OvenState.heating)
            gpio.change_intensity(0)
        elif command == command.START_HEATING and OvenState.on:
            logger.debug(f'On START_HEATING')
            OvenState.heating = True
            modbus.send_working_status(OvenState.heating)
        elif command == command.CANCEL:
            logger.debug(f'On CANCEL')
            OvenState.heating = False
            modbus.send_working_status(OvenState.heating)
            gpio.change_intensity(0)
        elif command == command.TOGGLE_TEMP_MODE:
            logger.debug(f'On TOGGLE_TEMP_MODE')
            OvenState.heating_status = [HeatingStatus.CURVE, HeatingStatus.DASHBOARD][OvenState.heating_status != HeatingStatus.DASHBOARD]
            modbus.send_control_status(OvenState.heating_status != HeatingStatus.DASHBOARD)

        OvenState.room_temp = i2c.read_temp()
        modbus.send_room_temp(OvenState.room_temp, retries=0)


def update_temperature():
    logger = logging.getLogger('debug')
    while True:
        time.sleep(2)
        internal = modbus.internal_temp()
        if internal is not None:
            OvenState.internal_temp = internal
        logger.debug(f'Internal temp is {internal}')

        if OvenState.heating_status != HeatingStatus.DASHBOARD:
            logger.debug(f'Heating mode is DASHBOARD. Not updating')
            continue

        ref = modbus.reference_temp()
        if ref is not None:
            OvenState.reference_temp = ref
        logger.debug(f'Updating reference_temp to {ref}')


def handle_heating():
    while True:
        time.sleep(2)
        if not OvenState.heating:
            continue

        if OvenState.heating_status == HeatingStatus.CURVE:
            threading.Thread(target=handle_reflow_curve, daemon=True).start()

        go_to_reference_temp(lambda: OvenState.heating and OvenState.heating_status != HeatingStatus.CURVE)


def go_to_reference_temp(pred) -> None:
    logger = logging.getLogger('debug')

    while pred() and abs(OvenState.internal_temp - OvenState.reference_temp) > .5:
        pid.update_reference(OvenState.reference_temp)
        logger.debug(f'Updated PID reference to {OvenState.reference_temp}')

        internal = modbus.internal_temp()
        if internal is None:
            continue

        OvenState.internal_temp = internal
        OvenState.intensity = round(pid.control(OvenState.internal_temp))
        logger.debug(f'Updated OvenState.intensity to {OvenState.intensity}')
        modbus.send_control_signal(OvenState.intensity)
        modbus.send_reference_temp(OvenState.reference_temp)
        gpio.change_intensity(OvenState.intensity)

        time.sleep(1)


def handle_reflow_curve():
    cur_time = 0
    _, fst_temp = settings.REFLOW_CURVE[0]

    pred = lambda: OvenState.heating and OvenState.heating_status == HeatingStatus.CURVE

    OvenState.reference_temp = fst_temp
    go_to_reference_temp(pred)

    for sec, temp in settings.REFLOW_CURVE[1:]:
        while sec - cur_time > 0 and pred():
            time.sleep(.5)

        if not pred():
            return

        OvenState.reference_temp = temp
        cur_time = sec


__all__ = ('handle_user_command', 'update_temperature', 'handle_heating')
