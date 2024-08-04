from flask import Flask, render_template
import RPi.GPIO as GPIO

app = Flask(__name__)

# Liste der GPIO-Pins, die auf Ihrem Raspberry Pi verfügbar sind
gpio_pins = [4, 17, 18, 27, 22, 23, 24, 25, 5, 6, 12, 13, 19, 16, 26, 20, 21]

# Richten Sie die GPIO-Pins ein
GPIO.setmode(GPIO.BCM)
for pin in gpio_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

@app.route('/')
def index():
    sensor_states = {}
    for pin in gpio_pins:
        try:
            state = GPIO.input(pin)
            sensor_states[pin] = state
        except RuntimeError:
            sensor_states[pin] = "Fehler"
    return render_template('scan.html', sensor_states=sensor_states)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5050)
    except KeyboardInterrupt:
        GPIO.cleanup()
