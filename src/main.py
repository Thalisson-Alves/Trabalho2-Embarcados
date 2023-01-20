import time
from modbus import Modbus


def main():
    mod = Modbus()
    print(mod.internal_temp)

if __name__ == '__main__':
    main()
