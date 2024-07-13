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
    pir_no_power_start_time = None

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 30:  # Ignorieren der Bewegungserkennung für die ersten 30 Sekunden
            if GPIO.input(SENSOR_PIN):
                log_message("Bewegung erkannt! Brief ist da.")
                last_signal_time = time.time()
                pir_no_power_start_time = None  # Reset if PIR has power
            else:
                # Check if the PIR sensor has no power
                if pir_no_power_start_time is None:
                    pir_no_power_start_time = time.time()
                
                # If the PIR has had no power for more than 10 seconds
                if time.time() - pir_no_power_start_time > 10:
                    log_message("Briefkasten ist offen.")
                else:
                    log_message("Keine Bewegung. Kein Brief.")

        time.sleep(1)  # Überprüfen Sie den Sensor jede Sekunde
except KeyboardInterrupt:
    GPIO.cleanup()
    log_message("Programm beendet.")
