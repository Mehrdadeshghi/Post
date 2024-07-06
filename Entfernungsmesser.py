import RPi.GPIO as GPIO
import time
import datetime
import subprocess
import os
from threading import Thread, Event

# Set the working directory to ensure file paths are correct
os.chdir('/home/mehrdad/Desktop/Post')

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_LED = 23  # Call to Action LED
GPIO_PIR = 25  # PIR sensor
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_LED, GPIO.OUT)
GPIO.setup(GPIO_PIR, GPIO.IN)
GPIO.output(GPIO_LED, GPIO.LOW)  # Initial state is OFF

# Log file path
logfile = "/home/mehrdad/Desktop/Post/distance_log.txt"

# Ensure log file exists
if not os.path.exists(logfile):
    open(logfile, 'w').close()

# Flag to indicate if motion is detected
motion_detected_flag = Event()

def distanz():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    StartZeit = time.time()
    StopZeit = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartZeit = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopZeit = time.time()
    TimeElapsed = StopZeit - StartZeit
    return (TimeElapsed * 34300) / 2

def get_cpu_temp():
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
    temp_str = result.stdout.strip()
    temp_value = temp_str.split('=')[1].split("'")[0]
    return float(temp_value)

def log_to_txt(timestamp, distance, cpu_temp, postchi, post, call_to_action):
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H:%M:%S")
    log_message = f"{date_str}, {time_str}, {distance:.1f} cm, {cpu_temp:.1f} °C, Postchi: {postchi}, Post: {post}, Call To Action: {call_to_action}\n"
    with open(logfile, "a") as file:
        file.write(log_message)

def check_motion(pin, duration=5, threshold=2):
    while True:
        motion_start_time = time.time()
        motion_detected_count = 0
        while time.time() - motion_start_time < duration:  # Check for motion over a period of 'duration' seconds
            if GPIO.input(pin):
                motion_detected_count += 1
            time.sleep(1)  # Check every 100 milliseconds
        if motion_detected_count >= threshold:  # Consider motion detected if it was detected more than 'threshold' times
            motion_detected_flag.set()
        else:
            motion_detected_flag.clear()
        time.sleep(1)  # Wait a bit before checking again

# Start a separate thread to check for motion
motion_thread = Thread(target=check_motion, args=(GPIO_PIR,))
motion_thread.daemon = True
motion_thread.start()

if __name__ == '__main__':
    try:
        print("Starte Messung...")
        letzte_entfernung = distanz()
        postchi = 0
        post = 0
        call_to_action = 0
        minute_start_time = time.time()
        
        cpu_temp = get_cpu_temp()
        initial_message = "Starte Messung..."
        print(initial_message)
        log_to_txt(datetime.datetime.now(), letzte_entfernung, cpu_temp, postchi, post, call_to_action)
        print("Initiale Entfernung: %.1f cm, CPU-Temperatur: %.1f°C" % (letzte_entfernung, cpu_temp))

        last_change_time = time.time()
        
        while True:
            if motion_detected_flag.is_set():
                print("Bewegung erkannt, Messungen pausiert.")
                GPIO.output(GPIO_LED, GPIO.LOW)  # Turn off LED when motion is detected
            else:
                abstand = distanz()
                current_time = time.time()
                elapsed_time = current_time - last_change_time
                elapsed_minute_time = current_time - minute_start_time
                cpu_temp = get_cpu_temp()

                if abs(abstand - letzte_entfernung) >= 2:
                    postchi += 1
                    letzte_entfernung = abstand
                    last_change_time = current_time
                    if postchi >= 5:
                        post += 1
                        postchi = 0
                        print(f"Postchi hat 5 erreicht. Post wurde um 1 erhöht. Post: {post}")
                        minute_start_time = current_time

                    if 0 < post < 5:
                        call_to_action = 1
                        GPIO.output(GPIO_LED, GPIO.HIGH)  # Turn ON LED
                    else:
                        call_to_action = 0
                        GPIO.output(GPIO_LED, GPIO.LOW)  # Turn OFF LED

                    log_to_txt(datetime.datetime.now(), abstand, cpu_temp, postchi, post, call_to_action)
                else:
                    if elapsed_minute_time >= 60:
                        if 0 < post < 5:
                            call_to_action = 1
                            GPIO.output(GPIO_LED, GPIO.HIGH)  # Turn ON LED
                        else:
                            call_to_action = 0
                            GPIO.output(GPIO_LED, GPIO.LOW)  # Turn OFF LED

                        print(f"Keine Änderung in der Entfernung seit mehr als einer Minute")
                        log_to_txt(datetime.datetime.now(), abstand, cpu_temp, postchi, post, call_to_action)
                        postchi = 0
                        minute_start_time = current_time

                    if elapsed_time >= 3600:
                        print("Keine Änderung in der Entfernung seit mehr als einer Stunde")
                        log_to_txt(datetime.datetime.now(), abstand, cpu_temp, postchi, post, call_to_action)
                        last_change_time = current_time
                    elif elapsed_time >= 60:
                        print("Keine Änderung in der Entfernung seit mehr als einer Minute")
                        log_to_txt(datetime.datetime.now(), abstand, cpu_temp, postchi, post, call_to_action)
                        last_change_time = current_time
                    else:
                        print("Gemessene Entfernung = %.1f cm, CPU-Temperatur: %.1f°C" % (abstand, cpu_temp))
                        log_to_txt(datetime.datetime.now(), abstand, cpu_temp, postchi, post, call_to_action)

            time.sleep(1)  # Set sleep time to 1 second for distance sensor frequency
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
        cpu_temp = get_cpu_temp()
        log_to_txt(datetime.datetime.now(), letzte_entfernung, cpu_temp, postchi, post, call_to_action)
        print(f"Gesamte Anzahl der Änderungen: Postchi: {postchi}, Post: {post}, Call To Action: {call_to_action}")
        GPIO.cleanup()
