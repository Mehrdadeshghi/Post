from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import time
import threading
import sqlite3
import datetime
import psutil
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN_1 = 25
PIR_PIN_2 = 24
GPIO.setup(PIR_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIR_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Global variables to store mailbox states
mailbox_1_state = "No Mail"
mailbox_2_state = "No Mail"

def monitor_mailboxes():
    global mailbox_1_state, mailbox_2_state
    while True:
        # Check Mehrdad sensor status
        mehrdad_status = GPIO.input(PIR_PIN_1)
        print(f"Checking Mehrdad sensor: {mehrdad_status}")  # Debugging output
        if mehrdad_status:
            time.sleep(0.1)  # Short wait to ensure signal is stable
            if GPIO.input(PIR_PIN_1):  # Double check
                if mailbox_1_state != "Mail Detected":
                    mailbox_1_state = "Mail Detected"
                    log_mail("Mehrdad")
                    socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'Mail Detected'})
                    print("Mehrdad: Movement detected")
        else:
            if mailbox_1_state != "No Mail":
                mailbox_1_state = "No Mail"
                socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'No Mail'})
                print("Mehrdad: No movement")

        # Check Rezvaneh sensor status
        rezvaneh_status = GPIO.input(PIR_PIN_2)
        print(f"Checking Rezvaneh sensor: {rezvaneh_status}")  # Debugging output
        if rezvaneh_status:
            time.sleep(0.1)  # Short wait to ensure signal is stable
            if GPIO.input(PIR_PIN_2):  # Double check
                if mailbox_2_state != "Mail Detected":
                    mailbox_2_state = "Mail Detected"
                    log_mail("Rezvaneh")
                    socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'Mail Detected'})
                    print("Rezvaneh: Movement detected")
        else:
            if mailbox_2_state != "No Mail":
                mailbox_2_state = "No Mail"
                socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'No Mail'})
                print("Rezvaneh: No movement")

        time.sleep(1)  # Check every second

def log_mail(sensor):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("INSERT INTO movements (sensor, timestamp) VALUES (?, ?)", 
              (sensor, datetime.datetime.now().replace(microsecond=0)))
    conn.commit()
    conn.close()
    print(f"Logged movement for {sensor}")

# Background thread to monitor mailboxes
threading.Thread(target=monitor_mailboxes, daemon=True).start()

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

    # All movements for the graph
    c.execute("SELECT timestamp FROM movements WHERE sensor=?", (sensor_name,))
    all_movements = c.fetchall()

    conn.close()

    # Format the timestamps for Chart.js
    all_movements_formatted = [datetime.datetime.strptime(movement[0], '%Y-%m-%d %H:%M:%S').isoformat() for movement in all_movements]

    return {
        "total_movements": total_movements,
        "last_24h_movements": last_24h_movements,
        "last_week_movements": last_week_movements,
        "last_month_movements": last_month_movements,
        "last_movement": last_movement,
        "last_10_movements": last_10_movements,
        "all_movements": all_movements_formatted
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
    return render_template('index.html', controllers=controllers)

@app.route('/controller/<ip>')
def controller(ip):
    sensors = [{"name": "Mehrdad", "pin": 25}, {"name": "Rezvaneh", "pin": 24}]
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
