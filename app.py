from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import time
import threading
import sqlite3
import datetime
from datetime import timedelta
import psutil
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN_1 = 24
PIR_PIN_2 = 25
GPIO.setup(PIR_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIR_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Global variables to store sensor states
sensor_1_state = "Inactive"
sensor_2_state = "Inactive"

def monitor_sensors():
    global sensor_1_state, sensor_2_state
    while True:
        # Check sensor 1 status
        sensor_1_status = GPIO.input(PIR_PIN_1)
        if sensor_1_status:
            time.sleep(0.1)
            if GPIO.input(PIR_PIN_1):
                if sensor_1_state != "Active":
                    sensor_1_state = "Active"
                    log_movement("PIR Sensor 1")
                    socketio.emit('movement', {'sensor': 'PIR Sensor 1', 'status': 'Active'})
        else:
            if sensor_1_state != "Inactive":
                sensor_1_state = "Inactive"
                socketio.emit('movement', {'sensor': 'PIR Sensor 1', 'status': 'Inactive'})

        # Check sensor 2 status
        sensor_2_status = GPIO.input(PIR_PIN_2)
        if sensor_2_status:
            time.sleep(0.1)
            if GPIO.input(PIR_PIN_2):
                if sensor_2_state != "Active":
                    sensor_2_state = "Active"
                    log_movement("PIR Sensor 2")
                    socketio.emit('movement', {'sensor': 'PIR Sensor 2', 'status': 'Active'})
        else:
            if sensor_2_state != "Inactive":
                sensor_2_state = "Inactive"
                socketio.emit('movement', {'sensor': 'PIR Sensor 2', 'status': 'Inactive'})

        time.sleep(1)

def log_movement(sensor_name):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("INSERT INTO movements (sensor, timestamp) VALUES (?, ?)", 
              (sensor_name, datetime.datetime.now().replace(microsecond=0)))
    conn.commit()
    conn.close()

# Background thread to monitor sensors
threading.Thread(target=monitor_sensors, daemon=True).start()

def get_aggregated_data(sensor_name):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()

    # Total movements
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=?", (sensor_name,))
    total_movements = c.fetchone()[0]

    # Last 24 hours
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=? AND timestamp >= datetime('now', '-1 day')", (sensor_name,))
    last_24h_movements = c.fetchone()[0]

    # Last week
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=? AND timestamp >= datetime('now', '-7 days')", (sensor_name,))
    last_week_movements = c.fetchone()[0]

    # Last month
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=? AND timestamp >= datetime('now', '-1 month')", (sensor_name,))
    last_month_movements = c.fetchone()[0]

    # Last movement
    c.execute("SELECT timestamp FROM movements WHERE sensor=? ORDER BY timestamp DESC LIMIT 1", (sensor_name,))
    last_movement = c.fetchone()
    last_movement = last_movement[0] if last_movement else None

    # Last 10 movements
    c.execute("SELECT timestamp FROM movements WHERE sensor=? ORDER BY timestamp DESC LIMIT 10", (sensor_name,))
    last_10_movements = c.fetchall()

    conn.close()

    return {
        "total_movements": total_movements,
        "last_24h_movements": last_24h_movements,
        "last_week_movements": last_week_movements,
        "last_month_movements": last_month_movements,
        "last_movement": last_movement,
        "last_10_movements": last_10_movements
    }

def get_system_info():
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    cpu_temps = psutil.sensors_temperatures()
    cpu_temp = cpu_temps.get('cpu-thermal', cpu_temps.get('coretemp', [{'current': None}]))[0]['current']
    net_io = psutil.net_io_counters()
    return {
        "system_name": "Raspberry Pi",
        "system_ip": "192.168.178.82",
        "system_uptime": str(uptime),
        "cpu_temp": cpu_temp,
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "network_upload": net_io.bytes_sent,
        "network_download": net_io.bytes_recv,
        "active_processes": len(psutil.pids())
    }

@app.route('/')
def index():
    controllers = [{"ip": "192.168.178.82", "name": "Controller 1"}]
    system_info = get_system_info()
    return render_template('index.html', controllers=controllers, system_info=system_info)

@app.route('/controller/<ip>')
def controller(ip):
    sensors = [{"name": "PIR Sensor 1", "pin": 24}, {"name": "PIR Sensor 2", "pin": 25}]
    return render_template('controller.html', sensors=sensors, controller_ip=ip)

@app.route('/sensor/<sensor_name>')
def sensor(sensor_name):
    data = get_aggregated_data(sensor_name)
    return render_template('sensor.html', sensor_name=sensor_name, data=data)

@app.route('/api/movements/<sensor_name>')
def api_movements(sensor_name):
    data = get_aggregated_data(sensor_name)
    return jsonify(data)

@app.route('/api/system_info')
def api_system_info():
    data = get_system_info()
    return jsonify(data)

@app.route('/system_info/<ip>')
def system_info(ip):
    data = get_system_info()
    return render_template('system_info.html', controller_ip=ip, data=data)

# Start socketio instead of app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
