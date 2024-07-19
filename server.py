from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import RPi.GPIO as GPIO
import time

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Device(db.Model):
    pin = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

db.create_all()

# Setup der GPIO Pins
pins = list(range(2, 28))  # Typische GPIO Pins auf einem Raspberry Pi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def check_pin(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin) == GPIO.HIGH

@app.route('/api/get_pin_states')
def get_pin_states():
    states = {pin: 'Kein Gerät' if check_pin(pin) else 'Gerät angeschlossen' for pin in pins}
    return jsonify(states)

@app.route('/api/get_devices')
def get_devices():
    devices = {device.pin: device.name for device in Device.query.all()}
    return jsonify(devices)

@app.route('/api/add_device', methods=['POST'])
def add_device():
    data = request.json
    pin = data.get('pin')
    name = data.get('name')
    if not pin or not name:
        return jsonify({'error': 'Invalid data'}), 400

    existing_device = Device.query.filter_by(pin=pin).first()
    if existing_device:
        return jsonify({'error': 'Device already exists'}), 409

    new_device = Device(pin=pin, name=name)
    db.session.add(new_device)
    db.session.commit()
    return jsonify({'success': 'Device added'}), 201

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        GPIO.cleanup()
