import RPi.GPIO as GPIO

# GPIO-Modus (BCM)
GPIO.setmode(GPIO.BCM)

# Definition der GPIO-Pins für die Segmente (A-G und DP)
segments = (17, 18, 27, 22, 23, 12, 16, 4)  # Reihenfolge: A, B, C, D, E, F, G, DP

# Segmente als Ausgang setzen und auf HIGH (1) schalten
for segment in segments:
    GPIO.setup(segment, GPIO.OUT)
    GPIO.output(segment, GPIO.HIGH)  # Schaltet alle Segmente dauerhaft ein

try:
    while True:
        pass  # Endlosschleife, um das Programm am Laufen zu halten
except KeyboardInterrupt:
    GPIO.cleanup()  # GPIO-Pins bereinigen, wenn das Programm mit Strg+C beendet wird
