from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import RPi.GPIO as GPIO
import time

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Device(db.Model):
    pin = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pins = list(range(2, 28))

def check_pin(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.setup(pin, GPIO.IN)
    pin_status = GPIO.input(pin) == GPIO.HIGH
    device = Device.query.filter_by(pin=pin).first()
    if device:
        return {'pin': pin, 'status': pin_status, 'name': device.name}
    return {'pin': pin, 'status': pin_status, 'name': None}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pin_states')
def pin_states():
    states = [check_pin(pin) for pin in pins]
    return jsonify(states)

@app.route('/api/add_device', methods=['POST'])
def add_device():
    pin = request.json.get('pin')
    name = request.json.get('name')
    if not pin or not name:
        return jsonify({'error': 'Missing data'}), 400
    existing_device = Device.query.filter_by(pin=pin).first()
    if existing_device:
        return jsonify({'error': 'Device already exists on this pin'}), 409
    new_device = Device(pin=pin, name=name)
    db.session.add(new_device)
    db.session.commit()
    return jsonify({'success': 'Device added', 'pin': pin, 'name': name}), 201

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        GPIO.cleanup()
