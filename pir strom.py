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
    last_signal_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 30:  # Ignorieren der Bewegungserkennung für die ersten 30 Sekunden
            if GPIO.input(SENSOR_PIN):
                log_message("Bewegung erkannt! Brief ist da.")
                last_signal_time = time.time()
            else:
                log_message("Keine Bewegung. Kein Brief.")

            # Überprüfen, ob innerhalb der letzten 60 Sekunden ein Signal empfangen wurde
            if time.time() - last_signal_time > 60:
                log_message("Warnung: Kein Signal vom PIR-Sensor empfangen. Überprüfen Sie die Stromversorgung.")
                last_signal_time = time.time()  # Zurücksetzen, um die Warnung nicht ständig zu wiederholen

        time.sleep(1)  # Überprüfen Sie den Sensor jede Sekunde
except KeyboardInterrupt:
    GPIO.cleanup()
    log_message("Programm beendet.")
