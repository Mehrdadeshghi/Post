from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import time
import threading
import sqlite3
import datetime
import matplotlib.pyplot as plt
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN_1 = 25
PIR_PIN_2 = 24
GPIO.setup(PIR_PIN_1, GPIO.IN)
GPIO.setup(PIR_PIN_2, GPIO.IN)

# Global variables to store sensor states
sensor_1_state = "No Motion"
sensor_2_state = "No Motion"

def monitor_sensors():
    global sensor_1_state, sensor_2_state
    while True:
        if GPIO.input(PIR_PIN_1):
            sensor_1_state = "Motion Detected"
            log_movement("Mehrdad")
            socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'Motion Detected'})
        else:
            sensor_1_state = "No Motion"
            socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'No Motion'})

        if GPIO.input(PIR_PIN_2):
            sensor_2_state = "Motion Detected"
            log_movement("Rezvaneh")
            socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'Motion Detected'})
        else:
            sensor_2_state = "No Motion"
            socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'No Motion'})

        time.sleep(1)  # Check every second

def log_movement(sensor):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("INSERT INTO movements (sensor, timestamp) VALUES (?, ?)", 
              (sensor, datetime.datetime.now()))
    conn.commit()
    conn.close()

# Background thread to monitor sensors
threading.Thread(target=monitor_sensors, daemon=True).start()

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
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("SELECT timestamp FROM movements WHERE sensor=? ORDER BY timestamp DESC LIMIT 10", (sensor_name,))
    movements = c.fetchall()
    conn.close()
    
    return render_template('sensor.html', sensor_name=sensor_name, movements=movements)

@app.route('/api/movements/<sensor_name>')
def api_movements(sensor_name):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("SELECT timestamp FROM movements WHERE sensor=? ORDER BY timestamp DESC LIMIT 10", (sensor_name,))
    movements = c.fetchall()
    conn.close()
    return jsonify(movements)

# Start socketio statt app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
