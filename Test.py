import RPi.GPIO as GPIO
import time

# GPIO Pins definieren
SENSOR_PIN = 25  # Pin für den Bewegungssensor

# GPIO-Modus festlegen (BCM)
GPIO.setmode(GPIO.BCM)

# GPIO-Pin als Eingang definieren
GPIO.setup(SENSOR_PIN, GPIO.IN)

try:
    print("Warte auf Bewegung...")
    while True:
        if GPIO.input(SENSOR_PIN):
            print("Bewegung erkannt! Brief ist da.")
        else:
            print("Keine Bewegung. Kein Brief.")
        time.sleep(1)  # Überprüfen Sie den Sensor jede Sekunde
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Programm beendet.")
