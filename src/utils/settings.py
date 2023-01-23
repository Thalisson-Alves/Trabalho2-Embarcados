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

LOG_CSV_FILE = os.getenv('LOG_CSV_FILE', '/tmp/log.csv')
DEBUG_CSV_FILE = os.getenv('LOG_CSV_FILE', '/tmp/log-debug.csv')

REFLOW_CSV = os.getenv(
    'REFLOW_CSV', 
    os.path.join(os.path.dirname(__file__), 'reflow.csv')
)

with open(REFLOW_CSV, encoding='utf-8') as f:
    # skip header
    f.readline()

    REFLOW_CURVE = [tuple(map(int, line.split(','))) for line in f]
