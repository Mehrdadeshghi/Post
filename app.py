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

# Define GPIO pins
SENSOR_PIN_Mehrdad = 25  # Pin for the motion sensor Mehrdad
SENSOR_PIN_Rezvaneh = 24  # Pin for the motion sensor Rezvaneh

# Set GPIO mode (BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO pin as input
GPIO.setup(SENSOR_PIN_Mehrdad, GPIO.IN)
GPIO.setup(SENSOR_PIN_Rezvaneh, GPIO.IN)

status = {
    "message": "Waiting for motion...",
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "movements": [],
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

@app.route('/bewegung', methods=['POST'])
def erfassen_bewegung():
    daten = request.get_json()
    if 'sensor' in daten and 'zeit' in daten:
        status['movements'].append(daten)
        print(f"Erfasste Bewegung: {daten}")
    else:
        print("Unvollständige Daten erhalten:", daten)
    return jsonify({"status": "erfasst"}), 200

@app.route('/movements')
def get_movements():
    return jsonify(status["movements"])

@app.route('/summary')
def get_summary():
    now = datetime.now()
    last_24_hours_movements = [m for m in status["movements"] if datetime.strptime(m['zeit'], "%Y-%m-%d %H:%M:%S") > now - timedelta(hours=24)]
    last_week_movements = [m for m in status["movements"] if datetime.strptime(m['zeit'], "%Y-%m-%d %H:%M:%S") > now - timedelta(weeks=1)]
    last_month_movements = [m for m in status["movements"] if datetime.strptime(m['zeit'], "%Y-%m-%d %H:%M:%S") > now - timedelta(days=30)]
    summary = {
        "total_movements": len(status["movements"]),
        "last_24_hours_movements": len(last_24_hours_movements),
        "last_week_movements": len(last_week_movements),
        "last_month_movements": len(last_month_movements),
        "last_motion_time": status["movements"][-1]['zeit'] if status["movements"] else "No movements detected"
    }
    return jsonify(summary)

@app.route('/hourly_movements')
def get_hourly_movements():
    now = datetime.now()
    hourly_movements = {str(hour): 0 for hour in range(24)}
    for movement in status["movements"]:
        movement_time = datetime.strptime(movement['zeit'], "%Y-%m-%d %H:%M:%S")
        if movement_time.date() == now.date():
            hour = movement_time.hour
            hourly_movements[str(hour)] += 1
    return jsonify(hourly_movements)

@app.route('/download/csv')
def download_csv():
    df = pd.DataFrame(status["movements"])
    output = io.BytesIO()
    df.to_csv(output, index_label="Index")
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='movements.csv', as_attachment=True)

@app.route('/download/excel')
def download_excel():
    df = pd.DataFrame(status["movements"])
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
        "Download": [status["network_activity"]["download"]],
        "Active Processes": [status["active_processes"]]
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
        "Download": [status["network_activity"]["download"]],
        "Active Processes": [status["active_processes"]]
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
            sensor_input_Mehrdad = GPIO.input(SENSOR_PIN_Mehrdad)
            sensor_input_Rezvaneh = GPIO.input(SENSOR_PIN_Rezvaneh)

            if sensor_input_Mehrdad == GPIO.HIGH:
                log_message("Motion detected: Mehrdad")
                sende_daten("Mehrdad")

            if sensor_input_Rezvaneh == GPIO.HIGH:
                log_message("Motion detected: Rezvaneh")
                sende_daten("Rezvaneh")

        time.sleep(1)

def sende_daten(sensor_name):
    daten = {'sensor': sensor_name, 'zeit': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    try:
        response = requests.post('http://localhost:5000/bewegung', json=daten)
        if response.status_code == 200:
            print(f"Bewegung von {sensor_name} erfasst und gesendet")
        else:
            print(f"Fehler beim Senden der Daten von {sensor_name}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")

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
