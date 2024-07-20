import RPi.GPIO as GPIO
import time
import requests

API_ENDPOINT = "http://192.168.178.82:5000/motion"

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def motion_detected(sensor):
    if sensor == 24:
        data = {"sensor": "Rezvaneh", "time": time.time()}
        print("Bewegung erkannt: Rezvaneh")
    elif sensor == 25:
        data = {"sensor": "Mehrdad", "time": time.time()}
        print("Bewegung erkannt: Mehrdad")
    
    # Senden der Daten an die API
    requests.post(API_ENDPOINT, json=data)

try:
    print("Einrichten der Bewegungserkennung für Sensor 24...")
    GPIO.add_event_detect(24, GPIO.RISING, callback=motion_detected, bouncetime=300)
    print("Bewegungserkennung für Sensor 24 erfolgreich eingerichtet.")
    
    print("Einrichten der Bewegungserkennung für Sensor 25...")
    GPIO.add_event_detect(25, GPIO.RISING, callback=motion_detected, bouncetime=300)
    print("Bewegungserkennung für Sensor 25 erfolgreich eingerichtet.")

    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
except RuntimeError as e:
    print(f"RuntimeError: {e}")
    GPIO.cleanup()
