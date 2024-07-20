from flask import Flask, render_template, jsonify
import threading
import time
from datetime import datetime
import RPi.GPIO as GPIO

app = Flask(__name__)

# Define sensor pins
MEHRDAD_PIN = 25
REZVANEH_PIN = 24

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MEHRDAD_PIN, GPIO.IN)
GPIO.setup(REZVANEH_PIN, GPIO.IN)

# Movements data structure
movements_mehrdad = []
movements_rezvaneh = []

def monitor_sensor(pin, movements_list, name):
    while True:
        if GPIO.input(pin) == GPIO.HIGH:
            movement_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            movements_list.append(movement_time)
            print(f"Motion detected on {name} at {movement_time}")
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movements/mehrdad')
def get_movements_mehrdad():
    return jsonify(movements_mehrdad)

@app.route('/movements/rezvaneh')
def get_movements_rezvaneh():
    return jsonify(movements_rezvaneh)

if __name__ == '__main__':
    # Start sensor monitoring threads
    threading.Thread(target=monitor_sensor, args=(MEHRDAD_PIN, movements_mehrdad, "Mehrdad"), daemon=True).start()
    threading.Thread(target=monitor_sensor, args=(REZVANEH_PIN, movements_rezvaneh, "Rezvaneh"), daemon=True).start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
