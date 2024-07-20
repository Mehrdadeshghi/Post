from gpiozero import MotionSensor
import time
import requests

API_ENDPOINT = "http://<deine_api_ip>:5000/motion"

pir_24 = MotionSensor(24)
pir_25 = MotionSensor(25)

def send_motion_data(sensor_name):
    data = {"sensor": sensor_name, "time": time.time()}
    print(f"Bewegung erkannt: {sensor_name}")
    requests.post(API_ENDPOINT, json=data)

pir_24.when_motion = lambda: send_motion_data("Rezvaneh")
pir_25.when_motion = lambda: send_motion_data("Mehrdad")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Programm beendet")
