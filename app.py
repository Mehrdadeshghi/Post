from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import time
import threading
import sqlite3
import datetime
from datetime import timedelta
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN_1 = 25
PIR_PIN_2 = 24
GPIO.setup(PIR_PIN_1, GPIO.IN)
GPIO.setup(PIR_PIN_2, GPIO.IN)

# Global variables to store mailbox states
mailbox_1_state = "No Mail"
mailbox_2_state = "No Mail"

def monitor_mailboxes():
    global mailbox_1_state, mailbox_2_state
    while True:
        if GPIO.input(PIR_PIN_1):
            mailbox_1_state = "Mail Detected"
            log_mail("Mehrdad")
            socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'Mail Detected'})
        else:
            mailbox_1_state = "No Mail"
            socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'No Mail'})

        if GPIO.input(PIR_PIN_2):
            mailbox_2_state = "Mail Detected"
            log_mail("Rezvaneh")
            socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'Mail Detected'})
        else:
            mailbox_2_state = "No Mail"
            socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'No Mail'})

        time.sleep(1)  # Check every second

def log_mail(sensor):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("INSERT INTO movements (sensor, timestamp) VALUES (?, ?)", 
              (sensor, datetime.datetime.now().replace(microsecond=0)))
    conn.commit()
    conn.close()

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

    return {
        "total_movements": total_movements,
        "last_24h_movements": last_24h_movements,
        "last_week_movements": last_week_movements,
        "last_month_movements": last_month_movements,
        "last_movement": last_movement,
        "last_10_movements": last_10_movements,
        "all_movements": all_movements
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

# Start socketio statt app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
