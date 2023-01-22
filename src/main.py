import time
import modbus
import gpio
import i2c
import pid
from oven_status import OvenStatus


def main():
    startup()

    try:
        _main()
    finally:
        shutdown()


def _main():
    while True:
        time.sleep(3)

        command = modbus.read_command()
        print(f'Received {command = }')

        if command is None: continue

        if command == command.OVEN_ON:
            OvenStatus.on = True
            modbus.send_system_status(OvenStatus.on)
        elif command == command.OVEN_OFF:
            OvenStatus.on = False
            OvenStatus.heating = False
            modbus.send_system_status(OvenStatus.on)
            modbus.send_working_status(OvenStatus.heating)
            gpio.change_intensity(0)
        elif command == command.START_HEATING and OvenStatus.on:
            OvenStatus.heating = True
            modbus.send_working_status(OvenStatus.heating)

            OvenStatus.reference_temp = modbus.reference_temp()
            pid.update_reference(OvenStatus.reference_temp)

            OvenStatus.internal_temp = modbus.internal_temp()
            pid.control(OvenStatus.internal_temp)
        elif command == command.CANCEL:
            OvenStatus.heating = False
            modbus.send_working_status(OvenStatus.heating)
            gpio.change_intensity(0)
        elif command == command.TOGGLE_TEMP_MODE:
            ...

        modbus.send_room_temp(i2c.read_temp(), retries=0)


def startup():
    modbus.init()

    gpio.setup()
    gpio.change_intensity(0)

    pid.config_constants(OvenStatus.p, OvenStatus.i, OvenStatus.d)
    # TODO: Stop everything - system_status, working_status, ...


def shutdown():
    modbus.close()

    gpio.change_intensity(0)
    # TODO: Stop everything - system_status, working_status, ...


if __name__ == '__main__':
    main()
