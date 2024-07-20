from flask import Flask, render_template
import RPi.GPIO as GPIO
import time
import threading

# Set up GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN_1 = 25
PIR_PIN_2 = 24
GPIO.setup(PIR_PIN_1, GPIO.IN)
GPIO.setup(PIR_PIN_2, GPIO.IN)

# Flask app setup
app = Flask(__name__)

# Global variables to store sensor states
sensor_1_state = "No Motion"
sensor_2_state = "No Motion"

def monitor_sensors():
    global sensor_1_state, sensor_2_state
    while True:
        if GPIO.input(PIR_PIN_1):
            sensor_1_state = "Motion Detected"
        else:
            sensor_1_state = "No Motion"
        
        if GPIO.input(PIR_PIN_2):
            sensor_2_state = "Motion Detected"
        else:
            sensor_2_state = "No Motion"
        
        time.sleep(1)  # Check every second

# Background thread to monitor sensors
threading.Thread(target=monitor_sensors, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html', sensor_1=sensor_1_state, sensor_2=sensor_2_state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
