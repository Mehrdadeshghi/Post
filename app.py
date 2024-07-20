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

# Dictionary to store movements
movements = {
    MEHRDAD_PIN: [],
    REZVANEH_PIN: []
}

def monitor_sensor(pin, name):
    while True:
        if GPIO.input(pin) == GPIO.HIGH:
            movements[pin].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(f"Motion detected on {name}")
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movements/<int:pin>')
def get_movements(pin):
    if pin in movements:
        return jsonify(movements[pin])
    else:
        return "Invalid sensor pin", 400

if __name__ == '__main__':
    # Start sensor monitoring threads
    threading.Thread(target=monitor_sensor, args=(MEHRDAD_PIN, "Mehrdad"), daemon=True).start()
    threading.Thread(target=monitor_sensor, args=(REZVANEH_PIN, "Rezvaneh"), daemon=True).start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
