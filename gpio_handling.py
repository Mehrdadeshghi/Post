import RPi.GPIO as GPIO
import time

class GPIOHandler:
    def __init__(self, sensor_pins):
        self.SENSOR_PINS = sensor_pins
        self.movement_detected_times = {pin: [] for pin in self.SENSOR_PINS}
        self.last_motion_time = {pin: None for pin in self.SENSOR_PINS}
        self.power_check_status = {pin: [] for pin in self.SENSOR_PINS}
        GPIO.setmode(GPIO.BCM)
        for pin in self.SENSOR_PINS:
            GPIO.setup(pin, GPIO.IN)

    def get_sensor_input(self, pin):
        return GPIO.input(pin)

    def cleanup(self):
        GPIO.cleanup()
