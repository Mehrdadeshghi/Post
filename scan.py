import RPi.GPIO as GPIO
from flask import Flask, render_template

app = Flask(__name__)

# Set up the GPIO pins
GPIO.setmode(GPIO.BCM)

# Define the pins you want to check
pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12, 7, 8, 25, 24, 23, 18, 15, 14]

def scan_pins():
    pin_status = {}
    for pin in pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
        try:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
            pin_status[pin] = 'Not Connected'
        except:
            pin_status[pin] = 'Connected'
        GPIO.setup(pin, GPIO.IN)
    return pin_status

@app.route('/')
def index():
    pin_status = scan_pins()
    return render_template('scan.html', pin_status=pin_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
