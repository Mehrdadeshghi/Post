import RPi.GPIO as GPIO
import time
from datetime import datetime
from flask import Flask, jsonify, Blueprint

# Initialize the Flask Blueprint for the sensor
sensor_bp = Blueprint('sensor', __name__)

# Define GPIO pins and settings
SENSOR_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

# Global variables to manage sensor state
movement_detected_times = []
last_motion_time = None
no_motion_threshold = 60

def log_message(message):
    """Log messages with current timestamp."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} - {message}")

def check_sensor():
    """Continuously check the sensor state and log any detected motion."""
    global last_motion_time, movement_detected_times
    while True:
        sensor_input = GPIO.input(SENSOR_PIN)
        current_time = time.time()

        if sensor_input == GPIO.HIGH:
            movement_detected_times.append(current_time)
            movement_detected_times = [t for t in movement_detected_times if current_time - t <= 10]

            if len(movement_detected_times) >= 2:
                log_message("Motion detected! There is mail.")
                movement_detected_times = []
                last_motion_time = current_time
        else:
            if last_motion_time and current_time - last_motion_time > no_motion_threshold:
                log_message("No motion detected for threshold period. Mailbox is open.")
                last_motion_time = None
        time.sleep(1)

if __name__ == '__main__':
    check_sensor()
