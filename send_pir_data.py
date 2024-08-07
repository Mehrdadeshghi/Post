import RPi.GPIO as GPIO
import requests
import json
import time

# Konfiguration des PIR-Sensors
PIR_PIN = 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Funktion zum Abrufen der Serialnummer
def get_serial():
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

# Funktion zum Abrufen der Sensor-ID aus der Datenbank
def get_sensor_id():
    serial_number = get_serial()
    # Verbindung zur Datenbank und Abruf der Sensor-ID (dieser Teil muss angepasst werden)
    # Dies ist nur ein Beispiel und setzt voraus, dass die Serialnummer als Sensor-ID verwendet wird.
    return serial_number

# Sensor-ID abrufen
sensor_id = get_sensor_id()

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
