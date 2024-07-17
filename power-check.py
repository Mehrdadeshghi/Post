import RPi.GPIO as GPIO
import time

# Pin-Nummerierung nach BCM verwenden
GPIO.setmode(GPIO.BCM)

# Pin 2 als Eingang festlegen
pin_number = 2
GPIO.setup(pin_number, GPIO.IN)

try:
    while True:
        # Den Status des Pins lesen
        if GPIO.input(pin_number) == GPIO.HIGH:
            print("Pin 2 ist HIGH - Strom wird gezogen.")
        else:
            print("Pin 2 ist LOW - Kein Strom wird gezogen.")

        # Um das Lesen zu verlangsamen
        time.sleep(1)

except KeyboardInterrupt:
    print("Programm wurde vom Benutzer gestoppt.")
    GPIO.cleanup()
