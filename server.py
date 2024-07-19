from flask import Flask, jsonify
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# Setup der GPIO Pins
pins = list(range(2, 28))  # Typische GPIO Pins auf einem Raspberry Pi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def check_pin(pin):
    # Pin als Ausgang setzen und auf HIGH setzen
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.1)  # Warte kurz, um den Pin zu stabilisieren

    # Pin als Eingang setzen und den Status lesen
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin) == GPIO.HIGH  # Gibt True zurück, wenn HIGH (kein Gerät angeschlossen)

@app.route('/api/get_pin_states')
def get_pin_states():
    states = {pin: 'Kein Gerät' if check_pin(pin) else 'Gerät angeschlossen' for pin in pins}
    return jsonify(states)

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        GPIO.cleanup()
