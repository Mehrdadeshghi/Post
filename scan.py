import RPi.GPIO as GPIO
import time

# Pin-Nummer des PIR-Sensors
pir_pin = 25

# GPIO Initialisierung
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_pin, GPIO.IN)

try:
    print("Warte auf Bewegung...")
    while True:
        if GPIO.input(pir_pin):
            print("Bewegung erkannt!")
            time.sleep(1)  # Einfache Entprellung / Wartezeit
        time.sleep(0.1)  # Kurze Verzögerung zwischen den Messungen
except KeyboardInterrupt:
    print("Programm gestoppt durch Benutzer")
finally:
    GPIO.cleanup()
