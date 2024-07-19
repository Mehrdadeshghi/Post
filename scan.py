import RPi.GPIO as GPIO
import time

# Verwendete GPIO Pins des Raspberry Pi
pins = list(range(2, 28))  # Typische GPIO Pins auf einem Raspberry Pi

# Initialisiere das GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def check_pin(pin):
    # Pin als Ausgang setzen und auf HIGH setzen
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.1)  # Warte kurz, um den Pin zu stabilisieren

    # Pin als Eingang setzen und den Status lesen
    GPIO.setup(pin, GPIO.IN)
    if GPIO.input(pin) == GPIO.HIGH:
        print(f"Pin {pin}: Kein Gerät.")
    else:
        print(f"Pin {pin}: Gerät angeschlossen.")

try:
    while True:
        # Überprüfe jeden Pin
        for pin in pins:
            try:
                check_pin(pin)
            except Exception as e:
                print(f"Error checking pin {pin}: {str(e)}")

        # Aufräumen
        GPIO.cleanup()

        # Warte eine Minute bevor die nächste Überprüfung beginnt
        time.sleep(60)

except KeyboardInterrupt:
    # Fange das Keyboard Interrupt Signal ab (z.B. durch Drücken von CTRL+C)
    GPIO.cleanup()
    print("Programm wurde durch Benutzer gestoppt.")

