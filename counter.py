import RPi.GPIO as GPIO
import time
from datetime import datetime

# GPIO Pins definieren
SENSOR_PIN = 23  # Pin für den Bewegungssensor

# GPIO-Modus festlegen (BCM)
GPIO.setmode(GPIO.BCM)

# GPIO-Pin als Eingang definieren
GPIO.setup(SENSOR_PIN, GPIO.IN)

# Logdatei öffnen
log_file_path = "/home/mehrdad/git/Post/logfile.log"

def log_message(message):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{current_time} - {message}"
    print(log_entry)
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry + "\n")

# Initiale Zeit zum Ignorieren der Bewegungserkennung setzen
start_time = time.time()
movement_count = 0

# Bewegungsbestätigungslogik
def is_movement_confirmed(pin, threshold=5, delay=0.2):
    count = 0
    for _ in range(threshold):
        if GPIO.input(pin):
            count += 1
        time.sleep(delay)
    return count >= threshold

try:
    log_message("Warte auf Bewegung...")
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 30:  # Ignorieren der Bewegungserkennung für die ersten 30 Sekunden
            if is_movement_confirmed(SENSOR_PIN):
                movement_count += 1
                log_message(f"Bewegung erkannt! Gesamtanzahl der Bewegungen: {movement_count}")
            else:
                if movement_count > 0:
                    movement_count = 0
                    log_message("Keine Bewegung. Zähler zurückgesetzt.")
        else:
            log_message("Erste 30 Sekunden. Ignoriere Bewegungserkennung.")
        time.sleep(1)  # Überprüfen Sie den Sensor jede Sekunde
except KeyboardInterrupt:
    GPIO.cleanup()
    log_message("Programm beendet.")
    log_message(f"Gesamtanzahl der Bewegungen: {movement_count}")
