from flask import Flask, jsonify, send_from_directory
import RPi.GPIO as GPIO

app = Flask(__name__, static_folder='static')

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pins = list(range(2, 28))
for pin in pins:
    GPIO.setup(pin, GPIO.IN)

@app.route('/api/get_pin_states')
def get_pin_states():
    states = {}
    for pin in pins:
        states[pin] = GPIO.input(pin)
    return jsonify(states)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
