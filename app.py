import RPi.GPIO as GPIO
import time
import os
import psutil
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, send_file, request
import pandas as pd
import io
import threading

class StateMachine:
    def __init__(self):
        self.state = "INIT"
        self.lock = threading.Lock()

    def set_state(self, state):
        with self.lock:
            print(f"Transitioning to {state} state.")
            self.state = state

    def get_state(self):
        with self.lock:
            return self.state

# Initialize the state machine
machine = StateMachine()

app = Flask(__name__)
app.config['DEBUG'] = True  # Activate debug mode

# Define GPIO pins for two PIR sensors
SENSOR_PIN_1 = 24  # Pin for the first motion sensor
SENSOR_PIN_2 = 25  # Pin for the second motion sensor

# Set GPIO mode (BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO pins as input
GPIO.setup(SENSOR_PIN_1, GPIO.IN)
GPIO.setup(SENSOR_PIN_2, GPIO.IN)

status = {
    "message": "Waiting for motion...",
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "movements_sensor_1": [],
    "movements_sensor_2": [],
    "cpu_temperature": 0,
    "system_uptime": 0,
    "network_activity": {"upload": 0, "download": 0},
    "active_processes": 0
}

movement_detected_times = []
last_motion_time = None
no_motion_threshold = 60  # Zeit in Sekunden ohne Bewegung für Mailbox open Zustand
power_check_interval = 10  # Intervall in Sekunden, um den PIR-Sensor zu überprüfen
last_power_check_time = time.time()
power_check_window = 30  # Zeitfenster, um den Stromstatus des PIR-Sensors zu überprüfen
power_check_status = []

def get_system_info():
    try:
        cpu_temperature = float(os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", ""))
    except Exception as e:
        print(f"Error fetching CPU temperature: {e}")
        cpu_temperature = 0  # Default value if the command fails
    try:
        uptime = os.popen("uptime -p").readline().strip()
    except Exception as e:
        print(f"Error fetching uptime: {e}")
        uptime = "N/A"
    try:
        net_stats = os.popen("ifstat -i eth0 1 1").readlines()[-1].strip().split()
        upload = float(net_stats[0])
        download = float(net_stats[1])
    except Exception as e:
        print(f"Error fetching network stats: {e}")
        upload = 0
        download = 0
    active_processes = len(psutil.pids())
    
    return cpu_temperature, uptime, upload, download, active_processes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/management')
def management():
    try:
        return render_template('management.html')
    except Exception as e:
        print(f"Error loading management page: {e}")
        return "Error loading management page"

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/system_info')
def system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    disk_usage = psutil.disk_usage('/').percent
    cpu_temperature, uptime, upload, download, active_processes = get_system_info()
    print(f"Fetched system info - CPU Temp: {cpu_temperature}, Uptime: {uptime}, Upload: {upload}, Download: {download}, Active Processes: {active_processes}")
    status.update({
        "cpu_temperature": cpu_temperature,
        "system_uptime": uptime,
        "network_activity": {"upload": upload, "download": download},
        "active_processes": active_processes
    })
    return jsonify({
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "cpu_temperature": cpu_temperature,
        "system_uptime": uptime,
        "network_activity": {"upload": upload, "download": download},
        "active_processes": active_processes
    })

@app.route('/status')
def get_status():
    return jsonify(status)

@app.route('/movements/<int:sensor_id>')
def get_movements(sensor_id):
    if sensor_id == 1:
        return jsonify(status["movements_sensor_1"])
    elif sensor_id == 2:
        return jsonify(status["movements_sensor_2"])
    else:
        return jsonify({"error": "Invalid sensor ID"}), 400

@app.route('/summary')
def get_summary():
    now = datetime.now()
    last_24_hours_movements_1 = [m for m in status["movements_sensor_1"] if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(hours=24)]
    last_week_movements_1 = [m for m in status["movements_sensor_1"] if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(weeks=1)]
    last_month_movements_1 = [m for m in status["movements_sensor_1"] if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(days=30)]

    last_24_hours_movements_2 = [m for m in status["movements_sensor_2"] if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(hours=24)]
    last_week_movements_2 = [m for m in status["movements_sensor_2"] if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(weeks=1)]
    last_month_movements_2 = [m for m in status["movements_sensor_2"] if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(days=30)]
    
    summary = {
        "sensor_1": {
            "total_movements": len(status["movements_sensor_1"]),
            "last_24_hours_movements": len(last_24_hours_movements_1),
            "last_week_movements": len(last_week_movements_1),
            "last_month_movements": len(last_month_movements_1),
            "last_motion_time": status["movements_sensor_1"][-1] if status["movements_sensor_1"] else "No movements detected"
        },
        "sensor_2": {
            "total_movements": len(status["movements_sensor_2"]),
            "last_24_hours_movements": len(last_24_hours_movements_2),
            "last_week_movements": len(last_week_movements_2),
            "last_month_movements": len(last_month_movements_2),
            "last_motion_time": status["movements_sensor_2"][-1] if status["movements_sensor_2"] else "No movements detected"
        }
    }
    return jsonify(summary)

@app.route('/hourly_movements')
def get_hourly_movements():
    now = datetime.now()
    hourly_movements_1 = {str(hour): 0 for hour in range(24)}
    for movement in status["movements_sensor_1"]:
        movement_time = datetime.strptime(movement, "%Y-%m-%d %H:%M:%S")
        if movement_time.date() == now.date():
            hour = movement_time.hour
            hourly_movements_1[str(hour)] += 1

    hourly_movements_2 = {str(hour): 0 for hour in range(24)}
    for movement in status["movements_sensor_2"]:
        movement_time = datetime.strptime(movement, "%Y-%m-%d %H:%M:%S")
        if movement_time.date() == now.date():
            hour = movement_time.hour
            hourly_movements_2[str(hour)] += 1
            
    return jsonify({"sensor_1": hourly_movements_1, "sensor_2": hourly_movements_2})

@app.route('/download/csv')
def download_csv():
    sensor_id = request.args.get('sensor_id', type=int)
    if sensor_id == 1:
        df = pd.DataFrame(status["movements_sensor_1"], columns=["Time"])
    elif sensor_id == 2:
        df = pd.DataFrame(status["movements_sensor_2"], columns=["Time"])
    else:
        return jsonify({"error": "Invalid sensor ID"}), 400

    output = io.BytesIO()
    df.to_csv(output, index_label="Index")
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name=f'movements_sensor_{sensor_id}.csv', as_attachment=True)

@app.route('/download/excel')
def download_excel():
    sensor_id = request.args.get('sensor_id', type=int)
    if sensor_id == 1:
        df = pd.DataFrame(status["movements_sensor_1"], columns=["Time"])
    elif sensor_id == 2:
        df = pd.DataFrame(status["movements_sensor_2"], columns=["Time"])
    else:
        return jsonify({"error": "Invalid sensor ID"}), 400

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index_label="Index")
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name=f'movements_sensor_{sensor_id}.xlsx', as_attachment=True)

def log_message(message, sensor):
    global movement_detected_times
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    status["message"] = message
    status["last_update"] = current_time
    if "motion detected" in message.lower():
        if sensor == 1:
            status["movements_sensor_1"].append(current_time)
        elif sensor == 2:
            status["movements_sensor_2"].append(current_time)
    print(f"{current_time} - {message} (Sensor {sensor})")

def check_sensor():
    global movement_detected_times, last_motion_time, last_power_check_time, power_check_status

    while True:
        current_state = machine.get_state()
        current_time = time.time()

        if current_state == "INIT":
            log_message("Initializing...", 0)
            machine.set_state("WAITING_FOR_MOTION")

        elif current_state == "WAITING_FOR_MOTION":
            sensor_input_1 = GPIO.input(SENSOR_PIN_1)
            sensor_input_2 = GPIO.input(SENSOR_PIN_2)

            # Update power check status
            if current_time - last_power_check_time > power_check_interval:
                last_power_check_time = current_time
                power_check_status.append((current_time, sensor_input_1, sensor_input_2))
                power_check_status = [status for status in power_check_status if current_time - status[0] <= power_check_window]

                # Check if both PIRs have no power
                if len(power_check_status) > 0 and all(status[1] == 0 and status[2] == 0 for status in power_check_status):
                    log_message("Mailbox is open. (Both PIRs have no power)", 0)
                    machine.set_state("MAILBOX_OPEN")

            if sensor_input_1 == GPIO.HIGH:
                handle_motion_detected(current_time, 1)
            elif sensor_input_2 == GPIO.HIGH:
                handle_motion_detected(current_time, 2)
            else:
                if last_motion_time and current_time - last_motion_time > no_motion_threshold:
                    log_message("Mailbox is open. (No motion detected for threshold period)", 0)
                    last_motion_time = None
                    machine.set_state("MAILBOX_OPEN")

        elif current_state == "MOTION_DETECTED":
            time.sleep(2)  # Simulate processing time
            machine.set_state("WAITING_FOR_MOTION")

        elif current_state == "MAILBOX_OPEN":
            time.sleep(2)  # Simulate processing time
            machine.set_state("WAITING_FOR_MOTION")

        time.sleep(1)

def handle_motion_detected(current_time, sensor):
    global movement_detected_times, last_motion_time
    movement_detected_times.append(current_time)
    movement_detected_times = [t for t in movement_detected_times if current_time - t <= 10]

    if len(movement_detected_times) >= 2:
        log_message("Motion detected! There is mail.", sensor)
        movement_detected_times = []
        last_motion_time = current_time
        machine.set_state("MOTION_DETECTED")

def cleanup_gpio():
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        from threading import Thread
        sensor_thread = Thread(target=check_sensor)
        sensor_thread.start()
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        cleanup_gpio()
    except Exception as e:
        print(f"Error: {e}")
        cleanup_gpio()
