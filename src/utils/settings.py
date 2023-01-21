import os

SO_DIR = os.getenv(
    'SO_DIR',
    os.path.join(
        os.path.dirname(__file__),
        '..', 'bin'
    )
)

RESISTOR_PIN = int(os.getenv('RESISTOR_PIN', '23'))
FAN_PIN = int(os.getenv('FAN_PIN', '24'))

SMBUS_PORT = int(os.getenv('SMBUS_PORT', '1'))
BME280_ADDR = int(os.getenv('SMBUS_PORT', '118'))
