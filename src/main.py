import time
import modbus
import gpio
import i2c


def main():
    startup()

    try:
        _main()
    finally:
        shutdown()


def _main():
    while True:
        time.sleep(0.5)

        command = modbus.read_command()
        print(f'Received {command.name = }')
        if command == command.OVEN_ON:
            modbus.send_system_status(True)
        elif command == command.OVEN_OFF:
            modbus.send_system_status(False)
            modbus.send_working_status(False)
            gpio.change_intensity(0)
        elif command == command.START_HEATING:
            ...
        elif command == command.CANCEL:
            ...
        elif command == command.TOGGLE_TEMP_MODE:
            ...


def startup():
    modbus.init()

    gpio.setup()
    gpio.change_intensity(0)


def shutdown():
    modbus.close()

    gpio.change_intensity(0)


if __name__ == '__main__':
    main()
