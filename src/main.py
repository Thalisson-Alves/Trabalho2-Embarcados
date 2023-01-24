import time
import modbus
import gpio
import i2c
import pid
from oven_status import OvenState
import curses
from screen import Screen
import threading
from utils import settings
import logging
from controller import *


def main():
    config_log()

    startup()

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


def config_log():
    # State logger
    formatter = logging.Formatter('%(asctime)s,%(message)s')
    handler = logging.FileHandler(settings.LOG_CSV_FILE)
    handler.setFormatter(formatter)
    logger = logging.getLogger('state')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Debug logger
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s %(message)s')
    handler = logging.FileHandler(settings.DEBUG_CSV_FILE)
    handler.setFormatter(formatter)
    logger = logging.getLogger('debug')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


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
    gpio.change_intensity(0)

    modbus.send_system_status(OvenState.on)
    modbus.send_working_status(OvenState.heating)

    modbus.close()


def log_state():
    while True:
        logging.getLogger('state').info(','.join(map(lambda x: f'{x:.2f}' if isinstance(x, float) else str(x), (OvenState.internal_temp,  OvenState.room_temp, OvenState.reference_temp, OvenState.intensity))))
        time.sleep(1)


if __name__ == '__main__':
    main()
