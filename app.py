import RPi.GPIO as GPIO
import time
from datetime import datetime
from flask import Flask, jsonify, render_template

app = Flask(__name__)
app.config['DEBUG'] = True  # Activate debug mode

# Define GPIO pins
SENSOR_PIN = 25  # Pin for the motion sensor

# Set GPIO mode (BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO pin as input
GPIO.setup(SENSOR_PIN, GPIO.IN)

status = {
    "message": "Waiting for motion...",
    "last_update": datetime.now().strftime("%H:%M:%S")
}

movement_count = 0
movement_window_start = time.time()
pir_no_power_start_time = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    return jsonify(status)

def log_message(message):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    status["message"] = message
    status["last_update"] = current_time
    print(f"{current_time} - {message}")

def check_sensor():
    global movement_count, movement_window_start, pir_no_power_start_time

    while True:
        if GPIO.input(SENSOR_PIN) == 0:
            if pir_no_power_start_time is None:
                pir_no_power_start_time = time.time()

            if time.time() - pir_no_power_start_time > 10:
                log_message("Mailbox is open.")
                pir_no_power_start_time = time.time()
        else:
            pir_no_power_start_time = None

            if GPIO.input(SENSOR_PIN):
                log_message("Motion detected! There is mail.")
                movement_count += 1

            if time.time() - movement_window_start > 10:
                if movement_count > 2:
                    log_message("You have mail")
                movement_count = 0
                movement_window_start = time.time()

        time.sleep(1)

if __name__ == '__main__':
    from threading import Thread
    sensor_thread = Thread(target=check_sensor)
    sensor_thread.start()
    app.run(host='0.0.0.0', port=5000)
