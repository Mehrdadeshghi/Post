import RPi.GPIO as GPIO
import time
from flask import Blueprint, render_template

sensor_bp = Blueprint('sensor', __name__)

# Setzen der GPIO-Pins
SENSOR_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

@sensor_bp.route('/')
def sensor_dashboard():
    return render_template('sensor.html')

def check_sensor():
    """Dieser Funktion würde in einem echten Szenario in einem separaten Thread laufen."""
    while True:
        if GPIO.input(SENSOR_PIN):
            print("Bewegung erkannt!")
        time.sleep(1)
