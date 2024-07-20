import RPi.GPIO as GPIO
import time
import requests

# GPIO-Modus (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# GPIO-Pins zuweisen
GPIO_PIR_Mehrdad = 25
GPIO_PIR_Rezvaneh = 24

# Setze GPIO-Richtung (IN / OUT)
GPIO.setup(GPIO_PIR_Mehrdad, GPIO.IN)
GPIO.setup(GPIO_PIR_Rezvaneh, GPIO.IN)

API_URL = 'http://localhost:5000/bewegung'

def sende_daten(sensor_name):
    daten = {'sensor': sensor_name, 'zeit': time.strftime("%Y-%m-%d %H:%M:%S")}
    try:
        response = requests.post(API_URL, json=daten)
        if response.status_code == 200:
            print(f"Bewegung von {sensor_name} erfasst und gesendet")
        else:
            print(f"Fehler beim Senden der Daten von {sensor_name}")
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")

def ueberwache_sensoren():
    print("Starte Bewegungsüberwachung...")
    try:
        while True:
            if GPIO.input(GPIO_PIR_Mehrdad):
                print("Bewegung erkannt: Mehrdad")
                sende_daten("Mehrdad")
                time.sleep(1)  # Kurze Pause, um Mehrfacherkennungen zu vermeiden
            if GPIO.input(GPIO_PIR_Rezvaneh):
                print("Bewegung erkannt: Rezvaneh")
                sende_daten("Rezvaneh")
                time.sleep(1)  # Kurze Pause, um Mehrfacherkennungen zu vermeiden
    except KeyboardInterrupt:
        print("Bewegungsüberwachung beendet")
        GPIO.cleanup()

if __name__ == "__main__":
    ueberwache_sensoren()
