from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import time

app = Flask(__name__, template_folder='templates', static_folder='static')

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pins = list(range(2, 28))  # Die GPIO-Pins, die überprüft werden

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pin_states')
def pin_states():
    states = {pin: check_pin(pin) for pin in pins}
    return jsonify(states)

def check_pin(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin) == GPIO.HIGH

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        GPIO.cleanup()
