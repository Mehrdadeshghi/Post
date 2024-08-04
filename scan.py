import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify
import datetime

app = Flask(__name__)

# Set up the GPIO pins
GPIO.setmode(GPIO.BCM)

# Define the pins you want to check
pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12, 7, 8, 25, 24, 23, 18, 15, 14]

# Sample data structure to store movements for each pin
movements_data = {pin: [] for pin in pins}

def scan_pins():
    pin_status = {}
    for pin in pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        status = GPIO.input(pin)
        if status == GPIO.LOW:
            pin_status[pin] = 'Connected'
            # Log the movement if it's a new movement (avoid duplicate entries)
            if not movements_data[pin] or (movements_data[pin] and movements_data[pin][-1] != datetime.datetime.now().isoformat()):
                movements_data[pin].append(datetime.datetime.now().isoformat())
        else:
            pin_status[pin] = 'Not Connected'
    return pin_status

@app.route('/')
def index():
    pin_status = scan_pins()
    return render_template('scan.html', pin_status=pin_status)

@app.route('/pin/<int:pin>')
def pin_detail(pin):
    return render_template('werte.html', pin=pin)

@app.route('/pin_status/<int:pin>')
def pin_status(pin):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    status = GPIO.input(pin)
    if status == GPIO.LOW:
        pin_status = 'Connected'
    else:
        pin_status = 'Not Connected'
    return jsonify({'pin': pin, 'status': pin_status})

@app.route('/movements/<int:pin>')
def get_movements(pin):
    return jsonify(movements_data[pin])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
