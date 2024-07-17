import RPi.GPIO as GPIO
import time
import os
import psutil
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, send_file
import pandas as pd
import io

class StateMachine:
    def __init__(self):
        self.state = "INIT"

    def set_state(self, state):
        print(f"Transitioning to {state} state.")
        self.state = state

    def get_state(self):
        return self.state

# Initialize the state machine
machine = StateMachine()

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
    "movements": [],
    "cpu_temperature": 0,
    "system_uptime": 0,
    "network_activity": {"upload": 0, "download": 0}
}

movement_detected_times = []
last_motion_time = None
no_motion_threshold = 60  # Zeit in Sekunden ohne Bewegung für Mailbox open Zustand
power_check_interval = 10  # Intervall in Sekunden, um den PIR-Sensor zu überprüfen
last_power_check_time = time.time()
power_check_window = 30  # Zeitfenster, um den Stromstatus des PIR-Sensors zu überprüfen
power_check_status = []

def get_system_info():
    cpu_temperature = float(os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", ""))
    uptime = os.popen("uptime -p").readline().strip()
    net_stats = os.popen("ifstat -i eth0 1 1").readlines()[-1].strip().split()
    upload = float(net_stats[0])
    download = float(net_stats[1])
    
    return cpu_temperature, uptime, upload, download

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/management')
def management():
    return render_template('management.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/system_info')
def system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    cpu_temperature, uptime, upload, download = get_system_info()
    status.update({
        "cpu_temperature": cpu_temperature,
        "system_uptime": uptime,
        "network_activity": {"upload": upload, "download": download}
    })
    return jsonify({
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "cpu_temperature": cpu_temperature,
        "system_uptime": uptime,
        "network_activity": {"upload": upload, "download": download}
    })

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
    output = io.BytesIO()
    df.to_csv(output, index_label="Index")
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='movements.csv', as_attachment=True)

@app.route('/download/excel')
def download_excel():
    df = pd.DataFrame(status["movements"], columns=["Time"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index_label="Index")
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='movements.xlsx', as_attachment=True)

@app.route('/download/system_info/csv')
def download_system_info_csv():
    system_info = {
        "CPU Temperature": [status["cpu_temperature"]],
        "System Uptime": [status["system_uptime"]],
        "Upload": [status["network_activity"]["upload"]],
        "Download": [status["network_activity"]["download"]]
    }
    df = pd.DataFrame(system_info)
    output = io.BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='system_info.csv', as_attachment=True)

@app.route('/download/system_info/excel')
def download_system_info_excel():
    system_info = {
        "CPU Temperature": [status["cpu_temperature"]],
        "System Uptime": [status["system_uptime"]],
        "Upload": [status["network_activity"]["upload"]],
        "Download": [status["network_activity"]["download"]]
    }
    df = pd.DataFrame(system_info)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='system_info.xlsx', as_attachment=True)

def log_message(message):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    status["message"] = message
    status["last_update"] = current_time
    if "mail" in message.lower() or "detected" in message.lower():
        status["movements"].append(current_time)
    print(f"{current_time} - {message}")

def check_sensor():
    global movement_detected_times, last_motion_time, last_power_check_time, power_check_status

    while True:
        current_state = machine.get_state()
        current_time = time.time()

        if current_state == "INIT":
            log_message("Initializing...")
            machine.set_state("WAITING_FOR_MOTION")

        elif current_state == "WAITING_FOR_MOTION":
            sensor_input = GPIO.input(SENSOR_PIN)

            # Update power check status
            if current_time - last_power_check_time > power_check_interval:
                last_power_check_time = current_time
                power_check_status.append((current_time, sensor_input))
                power_check_status = [status for status in power_check_status if current_time - status[0] <= power_check_window]

                # Check if PIR has no power
                if len(power_check_status) > 0 and all(status[1] == 0 for status in power_check_status):
                    log_message("Mailbox is open. (PIR has no power)")
                    machine.set_state("MAILBOX_OPEN")

            if sensor_input:
                movement_detected_times.append(current_time)
                movement_detected_times = [t for t in movement_detected_times if current_time - t <= 10]

                if len(movement_detected_times) >= 2:
                    log_message("Motion detected! There is mail.")
                    movement_detected_times = []
                    last_motion_time = current_time
                    machine.set_state("MOTION_DETECTED")
            else:
                if last_motion_time and current_time - last_motion_time > no_motion_threshold:
                    log_message("Mailbox is open.")
                    last_motion_time = None
                    machine.set_state("MAILBOX_OPEN")
                elif not last_motion_time:
                    log_message("Waiting for motion...")

        elif current_state == "MOTION_DETECTED":
            log_message("Processing motion...")
            time.sleep(2)  # Simulate processing time
            machine.set_state("WAITING_FOR_MOTION")

        elif current_state == "MAILBOX_OPEN":
            log_message("Processing mailbox open state...")
            time.sleep(2)  # Simulate processing time
            machine.set_state("WAITING_FOR_MOTION")

        time.sleep(1)

if __name__ == '__main__':
    from threading import Thread
    sensor_thread = Thread(target=check_sensor)
    sensor_thread.start()
    app.run(host='0.0.0.0', port=5000)
