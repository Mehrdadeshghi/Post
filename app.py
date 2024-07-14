import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
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
    "last_update": datetime.now().strftime("%H:%M:%S"),
    "movements": []
}

movement_count = 0
last_movement_time = None
pir_no_power_start_time = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    return jsonify(status)

@app.route('/movements')
def get_movements():
    return jsonify(status["movements"])

@app.route('/summary')
def get_summary():
    now = datetime.now()
    last_hour_movements = [m for m in status["movements"] if datetime.strptime(m, "%H:%M:%S") > now - timedelta(hours=1)]
    summary = {
        "total_movements": len(status["movements"]),
        "last_hour_movements": len(last_hour_movements)
    }
    return jsonify(summary)

@app.route('/hourly_movements')
def get_hourly_movements():
    now = datetime.now()
    hourly_movements = {str(hour): 0 for hour in range(24)}
    for movement in status["movements"]:
        movement_time = datetime.strptime(movement, "%H:%M:%S")
        if movement_time.date() == now.date():
            hour = movement_time.hour
            hourly_movements[str(hour)] += 1
    return jsonify(hourly_movements)

def log_message(message):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    status["message"] = message
    status["last_update"] = current_time
    if "mail" in message.lower() or "detected" in message.lower():
        status["movements"].append(current_time)
    print(f"{current_time} - {message}")

def check_sensor():
    global movement_count, last_movement_time, pir_no_power_start_time

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
                current_time = time.time()
                if last_movement_time is None or (current_time - last_movement_time > 10):
                    log_message("Motion detected! There is mail.")
                    last_movement_time = current_time
                else:
                    last_movement_time = current_time

        time.sleep(1)

if __name__ == '__main__':
    from threading import Thread
    sensor_thread = Thread(target=check_sensor)
    sensor_thread.start()
    app.run(host='0.0.0.0', port=5000)
