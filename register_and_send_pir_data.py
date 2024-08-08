import RPi.GPIO as GPIO
import requests
import json
import subprocess
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

# Funktion zum Abrufen der öffentlichen IP-Adresse
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return None

# Funktion zum Abrufen der Raspberry Pi ID anhand der Seriennummer
def get_raspberry_id(serial_number):
    try:
        response = requests.get(f'http://45.149.78.188:5002/get_raspberry_id?serial_number={serial_number}')
        if response.status_code == 200:
            return response.json()['raspberry_id']
        else:
            print(f"Error fetching raspberry_id: {response.json()}")
            return None
    except Exception as e:
        print(f"Error fetching raspberry_id: {e}")
        return None

# Funktion zum Registrieren des Sensors
def register_sensor(raspberry_id, location):
    data = {
        "raspberry_id": raspberry_id,
        "location": location
    }
    try:
        response = requests.post('http://45.149.78.188:5001/add_sensor', json=data)
        if response.status_code == 201:
            return response.json()['sensor_id']
        else:
            print(f"Error registering sensor: {response.json()}")
            return None
    except Exception as e:
        print(f"Error registering sensor: {e}")
        return None

# Systeminformationen sammeln
serial_number = get_serial()
public_ip = get_public_ip()
raspberry_id = get_raspberry_id(serial_number)

if raspberry_id:
    sensor_id = register_sensor(raspberry_id, "Briefkasten Standort 1")
    if sensor_id:
        print(f"Sensor registriert mit ID: {sensor_id}")

        # Funktion zum Senden der PIR-Daten
        def send_pir_data(movement_detected):
            data = {
                "sensor_id": sensor_id,
                "movement_detected": movement_detected
            }
            response = requests.post('http://45.149.78.188:5001/pir_data', json=data)
            print(response.status_code)
            print(response.text)

        print("PIR Sensor initialisiert...")

        try:
            previous_state = False
            while True:
                current_state = GPIO.input(PIR_PIN)
                if current_state and not previous_state:
                    print("Bewegung erkannt!")
                    send_pir_data(True)
                    previous_state = True
                elif not current_state and previous_state:
                    previous_state = False
                time.sleep(1)
        except KeyboardInterrupt:
            print("Beende...")
            GPIO.cleanup()
else:
    print("Raspberry ID konnte nicht abgerufen werden.")
