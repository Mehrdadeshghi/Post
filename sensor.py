import RPi.GPIO as GPIO
from flask import Blueprint, jsonify, render_template
from datetime import datetime

sensor_bp = Blueprint('sensor', __name__)

# GPIO-Pin-Konfiguration
SENSOR_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

# Globale Liste zur Speicherung der Bewegungszeiten
movements = []

def detect_movement(channel):
    """Wird aufgerufen, wenn eine Bewegung erkannt wird."""
    movement_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    movements.append(movement_time)
    print(f"Bewegung erkannt um {movement_time}")

# Bewegungsereignis konfigurieren
GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=detect_movement)

@sensor_bp.route('/')
def sensor_dashboard():
    return render_template('sensor.html')

@sensor_bp.route('/movements')
def movements_list():
    return jsonify(movements)

@sensor_bp.route('/status')
def status():
    last_movement = movements[-1] if movements else 'Keine Bewegungen erkannt'
    return jsonify({"status": "Aktiv", "last_movement": last_movement})

@sensor_bp.route('/summary')
def summary():
    total_movements = len(movements)
    return jsonify({
        "total_movements": total_movements,
        "last_movement": movements[-1] if movements else 'Keine Bewegungen erkannt'
    })

@sensor_bp.route('/hourly')
def hourly():
    hourly_counts = {str(i).zfill(2): 0 for i in range(24)}
    for movement in movements:
        hour = datetime.strptime(movement, "%Y-%m-%d %H:%M:%S").strftime('%H')
        hourly_counts[hour] += 1
    return jsonify(hourly_counts)
