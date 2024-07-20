import RPi.GPIO as GPIO
import time

MEHRDAD_PIN = 25
REZVANEH_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(MEHRDAD_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(REZVANEH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def check_pin(pin, name):
    print(f"Checking {name} on pin {pin}")
    try:
        while True:
            state = GPIO.input(pin)
            print(f"{name} State: {'HIGH' if state == GPIO.HIGH else 'LOW'}")
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()

# Test each sensor individually
check_pin(MEHRDAD_PIN, "Mehrdad")
check_pin(REZVANEH_PIN, "Rezvaneh")
