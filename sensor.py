import RPi.GPIO as GPIO
import time
from flask import Blueprint, jsonify
from datetime import datetime

sensor_bp = Blueprint('sensor', __name__)

SENSOR_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

# Globale Liste zur Speicherung der Bewegungszeiten
movements = []

def detect_movement():
    """Diese Funktion wird bei jeder Bewegung aufgerufen."""
    movement_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    movements.append({"time": movement_time})
    print(f"Bewegung erkannt um {movement_time}")

# Callback-Funktion zur Bewegungserkennung
def motion_detected(channel):
    detect_movement()

GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=motion_detected)

@sensor_bp.route('/movements')
def movements_list():
    """Liefert die Liste aller erkannten Bewegungen."""
    return jsonify(movements)

@sensor_bp.route('/status')
def status():
    """Liefert den aktuellen Status des Sensors."""
    last_movement = movements[-1]['time'] if movements else 'Keine Bewegungen erkannt'
    return jsonify({"status": "Aktiv", "last_movement": last_movement})

@sensor_bp.route('/summary')
def summary():
    """Gibt eine Zusammenfassung der Bewegungen zurück."""
    total_movements = len(movements)
    return jsonify({
        "total_movements": total_movements,
        "last_movement": movements[-1]['time'] if movements else 'Keine Bewegungen erkannt'
    })
