from gpiozero import MotionSensor
from time import sleep

# Liste der GPIO-Pins, an die deine PIR-Sensoren angeschlossen sind
pir_pins = [4, 17, 27]  # Beispiel-Pins

# Erstelle eine Liste von MotionSensor-Objekten
pir_sensors = [MotionSensor(pin) for pin in pir_pins]

try:
    while True:
        for index, sensor in enumerate(pir_sensors):
            if sensor.motion_detected:
                print(f"Bewegung erkannt an Sensor {index + 1} (Pin {pir_pins[index]})")
        sleep(1)  # Überprüfe jede Sekunde
except KeyboardInterrupt:
    print("Programm durch Benutzer gestoppt.")
