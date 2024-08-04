import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify
from datetime import datetime
import random

app = Flask(__name__)

# Set up the GPIO pins
GPIO.setmode(GPIO.BCM)

# Define the pins you want to check
pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12, 7, 8, 25, 24, 23, 18, 15, 14]

def scan_pins():
    pin_status = {}
    for pin in pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        status = GPIO.input(pin)
        if status == GPIO.LOW:
            pin_status[pin] = 'Connected'
        else:
            pin_status[pin] = 'Not Connected'
    return pin_status

def get_sensor_data(gpio):
    # Dummy data for the sensor
    total_movements = random.randint(100, 200)
    last_24_hours_movements = random.randint(10, 50)
    last_week_movements = random.randint(50, 100)
    last_month_movements = random.randint(100, 150)
    last_motion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    movements = [
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S")) for _ in range(10)
    ]
    return {
        'total_movements': total_movements,
        'last_24_hours_movements': last_24_hours_movements,
        'last_week_movements': last_week_movements,
        'last_month_movements': last_month_movements,
        'last_motion_time': last_motion_time,
        'movements': movements
    }

@app.route('/')
def index():
    pin_status = scan_pins()
    return render_template('scan.html', pin_status=pin_status)

@app.route('/sensor/<int:gpio>')
def sensor(gpio):
    sensor_data = get_sensor_data(gpio)
    return render_template('werte.html', gpio=gpio, data=sensor_data, enumerate=enumerate)

@app.route('/movements/<int:gpio>')
def movements(gpio):
    sensor_data = get_sensor_data(gpio)
    return jsonify(sensor_data['movements'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
