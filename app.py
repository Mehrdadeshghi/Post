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
GPIO.setup(MEHRDAD_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(REZVANEH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Movements data structure
movements_mehrdad = []
movements_rezvaneh = []

def monitor_sensor(pin, movements_list, name):
    last_state = GPIO.input(pin)
    print(f"Starting monitoring for {name} on pin {pin}")
    while True:
        try:
            current_state = GPIO.input(pin)
            if current_state == GPIO.HIGH and last_state == GPIO.LOW:
                movement_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                movements_list.append(movement_time)
                print(f"Motion detected on {name} at {movement_time}")
            elif current_state == GPIO.LOW:
                print(f"{name} sensor is LOW")
            else:
                print(f"{name} sensor is fluctuating")
            last_state = current_state
        except Exception as e:
            print(f"Error monitoring {name}: {e}")
        time.sleep(0.1)

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
