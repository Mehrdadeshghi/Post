from gpiozero import InputDevice
import time

# Der GPIO-Pin, an den der PIR-Sensor angeschlossen ist
power_pin = 25

# Erstellen eines InputDevice, um den Stromstatus zu lesen
sensor_power = InputDevice(power_pin)

try:
    while True:
        if sensor_power.is_active:
            print("PIR-Sensor hat Strom.")
        else:
            print("PIR-Sensor hat keinen Strom.")
        
        # Pause für 1 Sekunde, um das Lesen zu verlangsamen
        time.sleep(1)

except KeyboardInterrupt:
    print("Programm wurde vom Benutzer gestoppt.")

