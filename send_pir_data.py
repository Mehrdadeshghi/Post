import RPi.GPIO as GPIO
import requests
import json
import time

# Konfiguration des PIR-Sensors
PIR_PIN = 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Funktion zum Abrufen der Sensor-ID
# Angenommen, die Sensor-ID ist bekannt und wird manuell konfiguriert
sensor_id = 1  # Beispielwert, die tatsächliche sensor_id verwenden

# Endpunkt-URL
url = "http://45.149.78.188:5001/pir_data"
headers = {'Content-Type': 'application/json'}

# Funktion zum Senden der PIR-Daten
def send_pir_data(movement_detected):
    data = {
        "sensor_id": sensor_id,
        "movement_detected": movement_detected
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.status_code)
    print(response.text)

print("PIR Sensor initialisiert...")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("Bewegung erkannt!")
            send_pir_data(True)
        else:
            send_pir_data(False)
        time.sleep(5)
except KeyboardInterrupt:
    print("Beende...")
    GPIO.cleanup()
