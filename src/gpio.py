import RPi.GPIO as gpio

from utils.settings import FAN_PIN, RESISTOR_PIN


_fan_pwm = None
_resistor_pwm = None


def setup(frequency: int = 1000) -> None:
    global _fan_pwm, _resistor_pwm

    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(FAN_PIN, gpio.OUT)
    gpio.setup(RESISTOR_PIN, gpio.OUT)

    _fan_pwm = gpio.PWM(FAN_PIN, frequency)
    _resistor_pwm = gpio.PWM(RESISTOR_PIN, frequency)

    _fan_pwm.start(0)
    _resistor_pwm.start(0)


def change_intensity(control_signal: int) -> None:
    if control_signal > 0:
        _fan_pwm.ChangeDutyCycle(0)
        _resistor_pwm.ChangeDutyCycle(control_signal)
    elif control_signal < 0:
        _fan_pwm.ChangeDutyCycle(max(-control_signal, 40))
        _resistor_pwm.ChangeDutyCycle(0)
    else:
        _fan_pwm.ChangeDutyCycle(0)
        _resistor_pwm.ChangeDutyCycle(0)
