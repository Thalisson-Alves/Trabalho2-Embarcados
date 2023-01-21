import smbus2
import bme280

from utils.settings import BME280_ADDR, SMBUS_PORT

bus = smbus2.SMBus(SMBUS_PORT)
bme280.load_calibration_params(bus, BME280_ADDR)

def read_temp() -> float:
    return bme280.sample(bus, BME280_ADDR).temperature
