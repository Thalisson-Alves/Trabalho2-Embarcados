import time
import modbus
import gpio
import i2c
import pid
from oven_status import OvenState
from curses import wrapper
from screen import Screen


def main():
    startup()

    try:
        wrapper(Screen().run)
        # _main()
    except KeyboardInterrupt:
        ...
    finally:
        shutdown()


def _main():
    while True:
        time.sleep(3)

        command = modbus.read_command()
        print(f'Received {command = }')

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

            OvenState.reference_temp = modbus.reference_temp()
            pid.update_reference(OvenState.reference_temp)

            OvenState.internal_temp = modbus.internal_temp()
            pid.control(OvenState.internal_temp)
        elif command == command.CANCEL:
            OvenState.heating = False
            modbus.send_working_status(OvenState.heating)
            gpio.change_intensity(0)
        elif command == command.TOGGLE_TEMP_MODE:
            ...

        modbus.send_room_temp(i2c.read_temp(), retries=0)


def startup():
    modbus.init()

    gpio.setup()
    gpio.change_intensity(0)

    pid.config_constants(OvenState.p, OvenState.i, OvenState.d)
    # TODO: Stop everything - system_status, working_status, ...


def shutdown():
    modbus.close()

    gpio.change_intensity(0)
    # TODO: Stop everything - system_status, working_status, ...


if __name__ == '__main__':
    main()
