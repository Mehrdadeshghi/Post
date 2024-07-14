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

try:
    log_message("Warte auf Bewegung...")
    movement_count = 0
    movement_window_start = time.time()
    pir_no_power_start_time = None

    while True:
        # Prüfen, ob der PIR Strom hat
        if GPIO.input(SENSOR_PIN) == 0:
            if pir_no_power_start_time is None:
                pir_no_power_start_time = time.time()
            
            # Wenn der PIR-Sensor mehr als 10 Sekunden keinen Strom hat
            if time.time() - pir_no_power_start_time > 10:
                log_message("Briefkasten ist offen.")
                pir_no_power_start_time = time.time()  # Zurücksetzen, um die Meldung nicht kontinuierlich zu wiederholen
        else:
            pir_no_power_start_time = None  # Reset if PIR has power
            
            # Bewegungserkennung
            if GPIO.input(SENSOR_PIN):
                log_message("Bewegung erkannt! Brief ist da.")
                movement_count += 1
                
                # Überprüfen, ob mehr als 30 Bewegungen innerhalb von 1 Minute erkannt wurden
                if time.time() - movement_window_start <= 60:
                    if movement_count >= 30:
                        log_message("Du hast Post")
                        movement_count = 0  # Zurücksetzen nach der Benachrichtigung
                        movement_window_start = time.time()  # Zeitfenster zurücksetzen
                else:
                    # Zurücksetzen des Zählers und des Zeitfensters, wenn mehr als 1 Minute vergangen ist
                    movement_count = 1
                    movement_window_start = time.time()
            else:
                log_message("Keine Bewegung.")
                movement_count = 0  # Reset movement count if no movement detected

        time.sleep(1)  # Sensor jede Sekunde überprüfen
except KeyboardInterrupt:
    GPIO.cleanup()
    log_message("Programm beendet.")
