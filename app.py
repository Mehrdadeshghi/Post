from flask import Flask, render_template, jsonify
import threading
import time
from sensor_handling import SensorHandler, StateMachine
from gpio_handling import GPIOHandler

app = Flask(__name__)

# Initialize the GPIO handler with the relevant GPIO pins
sensor_pins = [24, 25]  # Add other pins if necessary
gpio_handler = GPIOHandler(sensor_pins)

# Initialize the state machine
state_machine = StateMachine()

# Initialize the sensor handler
sensor_handler = SensorHandler(gpio_handler, state_machine)

# Start monitoring sensors in a separate thread
sensor_thread = threading.Thread(target=sensor_handler.monitor_sensors)
sensor_thread.daemon = True
sensor_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify(sensor_handler.status)

@app.route('/movements')
def movements():
    return jsonify(sensor_handler.status["movements"])

@app.route('/summary')
def summary():
    # Prepare summary data for the dashboard
    summary = {}
    for pin in sensor_pins:
        summary[pin] = {
            "total_movements": len(sensor_handler.status["movements"][pin]),
            "last_24_hours_movements": len([t for t in sensor_handler.status["movements"][pin] if time.time() - t <= 86400]),
            "last_week_movements": len([t for t in sensor_handler.status["movements"][pin] if time.time() - t <= 604800]),
            "last_month_movements": len([t for t in sensor_handler.status["movements"][pin] if time.time() - t <= 2592000]),
            "last_motion_time": sensor_handler.gpio_handler.last_motion_time[pin]
        }
    return jsonify(summary)

@app.route('/movements/<int:pin>')
def movements_for_pin(pin):
    if pin in sensor_pins:
        return jsonify(sensor_handler.status["movements"][pin])
    else:
        return "Invalid sensor pin", 400

@app.route('/summary/<int:pin>')
def summary_for_pin(pin):
    if pin in sensor_pins:
        pin_summary = {
            "total_movements": len(sensor_handler.status["movements"][pin]),
            "last_24_hours_movements": len([t for t in sensor_handler.status["movements"][pin] if time.time() - t <= 86400]),
            "last_week_movements": len([t for t in sensor_handler.status["movements"][pin] if time.time() - t <= 604800]),
            "last_month_movements": len([t for t in sensor_handler.status["movements"][pin] if time.time() - t <= 2592000]),
            "last_motion_time": sensor_handler.gpio_handler.last_motion_time[pin]
        }
        return jsonify(pin_summary)
    else:
        return "Invalid sensor pin", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
