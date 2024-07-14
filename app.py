import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, send_file
import pandas as pd
import io

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
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "movements": []
}

movement_detected_times = []
last_motion_time = None

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
    last_hour_movements = [m for m in status["movements"] if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(hours=1)]
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
        movement_time = datetime.strptime(movement, "%Y-%m-%d %H:%M:%S")
        if movement_time.date() == now.date():
            hour = movement_time.hour
            hourly_movements[str(hour)] += 1
    return jsonify(hourly_movements)

@app.route('/download/csv')
def download_csv():
    df = pd.DataFrame(status["movements"], columns=["Time"])
    output = io.StringIO()
    df.to_csv(output, index_label="Index")
    output.seek(0)
    return send_file(output, mimetype='text/csv', attachment_filename='movements.csv', as_attachment=True)

@app.route('/download/excel')
def download_excel():
    df = pd.DataFrame(status["movements"], columns=["Time"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index_label="Index")
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', attachment_filename='movements.xlsx', as_attachment=True)

def log_message(message):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    status["message"] = message
    status["last_update"] = current_time
    if "mail" in message.lower() or "detected" in message.lower():
        status["movements"].append(current_time)
    print(f"{current_time} - {message}")

def check_sensor():
    global movement_detected_times, last_motion_time

    while True:
        sensor_input = GPIO.input(SENSOR_PIN)
        current_time = time.time()
        
        if sensor_input:
            movement_detected_times.append(current_time)
            movement_detected_times = [t for t in movement_detected_times if current_time - t <= 10]
            
            if len(movement_detected_times) >= 2:
                log_message("Motion detected! There is mail.")
                movement_detected_times = []
                last_motion_time = current_time
        else:
            if last_motion_time and current_time - last_motion_time > 10:
                log_message("Mailbox is open.")
                last_motion_time = None

        time.sleep(1)

if __name__ == '__main__':
    from threading import Thread
    sensor_thread = Thread(target=check_sensor)
    sensor_thread.start()
    app.run(host='0.0.0.0', port=5000)
