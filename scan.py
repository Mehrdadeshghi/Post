import RPi.GPIO as GPIO
import time

# Liste der Pins, die auf den meisten Raspberry Pi Modellen verfügbar sind
pins = list(range(2, 28))

# Initialisiere das GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def scan_pins():
    for pin in pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Setze den internen Pull-Down-Widerstand
        time.sleep(0.1)  # Kurze Verzögerung zum Stabilisieren des Eingangs
        if GPIO.input(pin) == GPIO.HIGH:
            print(f"Pin {pin}: Möglicherweise ist ein Gerät angeschlossen.")
        else:
            print(f"Pin {pin}: Kein Gerät angeschlossen.")

try:
    print("Scanne alle verfügbaren Pins...")
    scan_pins()
except KeyboardInterrupt:
    print("Scannen durch Benutzer abgebrochen.")
finally:
    GPIO.cleanup()

