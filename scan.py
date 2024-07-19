import RPi.GPIO as GPIO
import time

# Verwendete GPIO Pins des Raspberry Pi
pins = list(range(2, 28))  # Typische GPIO Pins auf einem Raspberry Pi

# Initialisiere das GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def check_pin(pin):
    # Pin als Ausgang setzen und auf LOW setzen
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)  # Warte kurz, um den Pin zu stabilisieren

    # Pin als Eingang setzen und den Status lesen
    GPIO.setup(pin, GPIO.IN)
    if GPIO.input(pin) == GPIO.LOW:
        print(f"Pin {pin}: Kein Gerät angeschlossen oder es hält den Zustand nicht.")
    else:
        print(f"Pin {pin}: Möglicherweise ist ein Gerät angeschlossen.")

# Überprüfe jeden Pin
for pin in pins:
    try:
        check_pin(pin)
    except Exception as e:
        print(f"Fehler beim Überprüfen von Pin {pin}: {str(e)}")

# Aufräumen
GPIO.cleanup()
