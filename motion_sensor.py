import RPi.GPIO as GPIO
import time
import requests

API_ENDPOINT = "http://<deine_api_ip>:5000/motion"

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)
GPIO.setup(25, GPIO.IN)

def motion_detected(sensor):
    if sensor == 24:
        data = {"sensor": "Rezvaneh", "time": time.time()}
        print("Bewegung erkannt: Rezvaneh")
    elif sensor == 25:
        data = {"sensor": "Mehrdad", "time": time.time()}
        print("Bewegung erkannt: Mehrdad")
    
    # Senden der Daten an die API
    requests.post(API_ENDPOINT, json=data)

GPIO.add_event_detect(24, GPIO.RISING, callback=motion_detected)
GPIO.add_event_detect(25, GPIO.RISING, callback=motion_detected)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
