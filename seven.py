import RPi.GPIO as GPIO
import time

# GPIO-Modus (BCM)
GPIO.setmode(GPIO.BCM)

# Definition der GPIO-Pins für die Segmente (A-G und DP)
segments = (17, 18, 27, 22, 23, 12, 16, 4)  # Reihenfolge: A, B, C, D, E, F, G, DP

# Segmente als Ausgang setzen
for segment in segments:
    GPIO.setup(segment, GPIO.OUT)
    GPIO.output(segment, 0)

# Segment-Muster für Ziffern definieren
num = {' ': (0, 0, 0, 0, 0, 0, 0),
       '0': (1, 1, 1, 1, 1, 1, 0),
       '1': (0, 1, 1, 0, 0, 0, 0),
       '2': (1, 1, 0, 1, 1, 0, 1),
       '3': (1, 1, 1, 1, 0, 0, 1),
       '4': (0, 1, 1, 0, 0, 1, 1),
       '5': (1, 0, 1, 1, 0, 1, 1),
       '6': (1, 0, 1, 1, 1, 1, 1),
       '7': (1, 1, 1, 0, 0, 0, 0),
       '8': (1, 1, 1, 1, 1, 1, 1),
       '9': (1, 1, 1, 1, 0, 1, 1)}

# Funktion zur Anzeige einer Ziffer auf dem 1-stelligen Display
def display_number(number):
    for loop in range(0, 7):
        GPIO.output(segments[loop], num[number][loop])

try:
    while True:
        for i in range(10):
            display_number(str(i))
            time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
