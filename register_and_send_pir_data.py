import RPi.GPIO as GPIO
import requests
import json
import subprocess
import time

# Liste aller möglichen GPIO-Pins, die geprüft werden sollen
GPIO_PINS = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12, 7, 8, 25, 24, 23, 18, 15, 14]

# Funktion zum Abrufen der Serialnummer
def get_serial():
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26].strip()
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

# Funktion zum Senden der PIR-Daten
def send_pir_data(sensor_id, movement_detected):
    data = {
        "sensor_id": sensor_id,
        "movement_detected": movement_detected
    }
    try:
        response = requests.post('http://45.149.78.188:5001/pir_data', json=data)
        print(f"Data sent: {data}, Response: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending PIR data: {e}")

# Funktion zum Scannen der GPIO-Pins
def scan_pins():
    pin_status = {}
    for pin in GPIO_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        status = GPIO.input(pin)
        if status == GPIO.LOW:
            pin_status[pin] = 'Connected'
        else:
            pin_status[pin] = 'Not Connected'
    return pin_status

# Systeminformationen sammeln
serial_number = get_serial()
print(f"Serial Number: {serial_number}")
public_ip = get_public_ip()
raspberry_id = get_raspberry_id(serial_number)

if raspberry_id:
    sensors = []
    GPIO.setmode(GPIO.BCM)

    # Scanne alle möglichen GPIO-Pins
    pin_status = scan_pins()
    for pin, status in pin_status.items():
        if status == 'Connected':
            location = f"Sensor at GPIO {pin}"
            sensor_id = register_sensor(raspberry_id, location)
            if sensor_id:
                sensors.append({
                    "pin": pin,
                    "sensor_id": sensor_id,
                    "location": location
                })
                print(f"Sensor registriert mit ID: {sensor_id} an PIN: {pin}")

    if sensors:
        print("PIR Sensoren initialisiert...")

        try:
            previous_states = {sensor['pin']: False for sensor in sensors}
            while True:
                for sensor in sensors:
                    current_state = GPIO.input(sensor['pin'])
                    if current_state and not previous_states[sensor['pin']]:
                        print(f"Bewegung erkannt an PIN: {sensor['pin']}, Location: {sensor['location']}")
                        send_pir_data(sensor['sensor_id'], True)
                        previous_states[sensor['pin']] = True
                    elif not current_state and previous_states[sensor['pin']]:
                        print(f"Keine Bewegung mehr erkannt an PIN: {sensor['pin']}, Location: {sensor['location']}")
                        send_pir_data(sensor['sensor_id'], False)
                        previous_states[sensor['pin']] = False
                time.sleep(1)
        except KeyboardInterrupt:
            print("Beende...")
            GPIO.cleanup()
    else:
        print("Keine Sensoren konnten registriert werden.")
else:
    print("Raspberry ID konnte nicht abgerufen werden.")
