import RPi.GPIO as GPIO
import time
from datetime import datetime

# GPIO Pins definieren
SENSOR_PIN_1 = 24  # Pin für den ersten Bewegungssensor
SENSOR_PIN_2 = 25  # Pin für den zweiten Bewegungssensor

# GPIO-Modus festlegen (BCM)
GPIO.setmode(GPIO.BCM)

# GPIO-Pins als Eingang definieren
GPIO.setup(SENSOR_PIN_1, GPIO.IN)
GPIO.setup(SENSOR_PIN_2, GPIO.IN)

# Logdatei öffnen
log_file_path = "/home/mehrdad/git/Post/logfile.log"

def log_message(message):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    log_entry = f"{current_time} - {message}"
    print(log_entry)
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry + "\n")

# Initiale Zeit zum Ignorieren der Bewegungserkennung setzen
start_time = time.time()

try:
    log_message("Warte auf Bewegung...")
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 30:  # Ignorieren der Bewegungserkennung für die ersten 30 Sekunden
            sensor_1_state = GPIO.input(SENSOR_PIN_1)
            sensor_2_state = GPIO.input(SENSOR_PIN_2)
            if sensor_1_state:
                log_message("Bewegung erkannt! Brief ist da. (GPIO24)")
            if sensor_2_state:
                log_message("Bewegung erkannt! Brief ist da. (GPIO25)")
            if not sensor_1_state and not sensor_2_state:
                log_message("Keine Bewegung. Kein Brief.")
        time.sleep(1)  # Überprüfen Sie den Sensor jede Sekunde
except KeyboardInterrupt:
    GPIO.cleanup()
    log_message("Programm beendet.")
