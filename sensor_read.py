import RPi.GPIO as GPIO
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)  # Rezvaneh
GPIO.setup(25, GPIO.IN)  # Mehrdad

@app.route('/bewegungen', methods=['GET'])
def get_bewegungen():
    rezvaneh = GPIO.input(24)
    mehrdad = GPIO.input(25)
    return jsonify({'Rezvaneh': rezvaneh, 'Mehrdad': mehrdad})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
