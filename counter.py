import RPi.GPIO as GPIO
import time
from datetime import datetime

# GPIO Pins definieren
SENSOR_PIN = 25  # Pin für den Bewegungssensor

# GPIO-Modus festlegen (BCM)
GPIO.setmode(GPIO.BCM)

# GPIO-Pin als Eingang definieren
GPIO.setup(SENSOR_PIN, GPIO.IN)

# Logdatei öffnen
log_file_path = "/path/to/your/logfile.log"

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

try:
    log_message("Warte auf Bewegung...")
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 30:  # Ignorieren der Bewegungserkennung für die ersten 30 Sekunden
            if GPIO.input(SENSOR_PIN):
                movement_count += 1
                log_message(f"Bewegung erkannt! Gesamtanzahl der Bewegungen: {movement_count}")
        time.sleep(1)  # Überprüfen Sie den Sensor jede Sekunde
except KeyboardInterrupt:
    GPIO.cleanup()
    log_message("Programm beendet.")
    log_message(f"Gesamtanzahl der Bewegungen: {movement_count}")
