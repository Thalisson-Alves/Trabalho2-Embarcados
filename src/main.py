import time
import modbus
import gpio
import i2c
import pid
from oven_status import OvenState, HeatingStatus
import curses
from screen import Screen
import threading
from utils import settings
import logging


def main():
    # TODO: Refactor this file
    # TODO: Add logs to a debug file
    startup()
    logging.basicConfig(
        filename=settings.LOG_CSV_FILE, 
        encoding='utf-8', 
        level=logging.INFO, 
        format='%(asctime)s,%(message)s', 
        datefmt='%d/%m/%Y %I:%M:%S'
    )

    threads = [
        threading.Thread(target=log_state, daemon=True),
        threading.Thread(target=handle_heating, daemon=True),
        threading.Thread(target=update_temperature, daemon=True),
        threading.Thread(target=handle_user_command, daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        curses.wrapper(Screen().run)
    except KeyboardInterrupt:
        ...
    except curses.error:
        msg = 'Aumente o tamanho do terminal e tente novamente!'
        print('*' * len(msg))
        print(msg)
        print('*' * len(msg))
    finally:
        shutdown()


def handle_user_command():
    while True:
        command = modbus.read_command()

        if command is None: continue

        if command == command.OVEN_ON:
            OvenState.on = True
            modbus.send_system_status(OvenState.on)
        elif command == command.OVEN_OFF:
            OvenState.on = False
            OvenState.heating = False
            modbus.send_system_status(OvenState.on)
            modbus.send_working_status(OvenState.heating)
            gpio.change_intensity(0)
        elif command == command.START_HEATING and OvenState.on:
            OvenState.heating = True
            modbus.send_working_status(OvenState.heating)
        elif command == command.CANCEL:
            OvenState.heating = False
            modbus.send_working_status(OvenState.heating)
            gpio.change_intensity(0)
        elif command == command.TOGGLE_TEMP_MODE:
            OvenState.heating_status = [HeatingStatus.CURVE, HeatingStatus.DASHBOARD][OvenState.heating_status != HeatingStatus.DASHBOARD]
            modbus.send_control_status(OvenState.heating_status != HeatingStatus.DASHBOARD)

        OvenState.room_temp = i2c.read_temp()
        modbus.send_room_temp(OvenState.room_temp, retries=0)


def update_temperature():
    while True:
        OvenState.internal_temp = modbus.internal_temp()

        if OvenState.heating_status != HeatingStatus.DASHBOARD:
            continue
        OvenState.reference_temp = modbus.reference_temp()


def handle_heating():
    while True:
        time.sleep(0.5)
        if not OvenState.heating:
            continue

        if OvenState.heating_status == HeatingStatus.CURVE:
            handle_reflow_curve()

        go_to_reference_temp(lambda: OvenState.heating and OvenState.heating_status != HeatingStatus.CURVE)


def go_to_reference_temp(pred) -> None:
    while pred() and OvenState.internal_temp != temp:
        pid.update_reference(OvenState.reference_temp)
        internal = modbus.internal_temp()
        if internal is not None:
            OvenState.internal_temp = internal

        OvenState.intensity = pid.control(internal)
        modbus.send_control_signal(OvenState.intensity)
        modbus.send_reference_temp(OvenState.reference_temp)
        gpio.change_intensity(OvenState.intensity)

        time.sleep(0.5)


def handle_reflow_curve():
    cur_time = 0
    fst_sec, fst_temp = settings.REFLOW_CURVE[0]

    pred = lambda: OvenState.heating and OvenState.heating_status == HeatingStatus.CURVE

    OvenState.reference_temp = fst_temp
    go_to_reference_temp(fst_temp, pred)

    for sec, temp in settings.REFLOW_CURVE:
        while sec - cur_time > 0 and pred():
            time.sleep(.5)

        if not pred():
            return

        OvenState.reference_temp = temp
        cur_time = sec


def startup():
    modbus.init()
    modbus.send_system_status(OvenState.on)
    modbus.send_working_status(OvenState.heating)

    OvenState.internal_temp = modbus.internal_temp()
    OvenState.reference_temp = modbus.reference_temp()
    OvenState.room_temp = i2c.read_temp()

    gpio.setup()
    gpio.change_intensity(0)

    pid.config_constants(OvenState.p, OvenState.i, OvenState.d)



def shutdown():
    modbus.close()

    gpio.change_intensity(0)

    modbus.send_system_status(OvenState.on)
    modbus.send_working_status(OvenState.heating)


def log_state():
    while True:
        logging.getLogger().info(','.join(map(lambda x: f'{x:.2f}' if isinstance(x, float) else str(x), (OvenState.internal_temp,  OvenState.room_temp, OvenState.reference_temp, OvenState.intensity))))
        time.sleep(1)


if __name__ == '__main__':
    main()
