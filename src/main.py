import time
import modbus


def main():
    startup()

    try:
        print(modbus.internal_temp())
    finally:
        shutdown()


def startup():
    modbus.init()


def shutdown():
    modbus.close()


if __name__ == '__main__':
    main()
