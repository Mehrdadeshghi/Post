from flask import Flask, render_template, jsonify, send_file
import RPi.GPIO as GPIO
import time
import threading
import sqlite3
import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN_1 = 25
PIR_PIN_2 = 24
GPIO.setup(PIR_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIR_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Global variables to store mailbox states
mailbox_1_state = "No Mail"
mailbox_2_state = "No Mail"

def monitor_mailboxes():
    global mailbox_1_state, mailbox_2_state
    while True:
        # Check Mailbox 1 sensor status
        mailbox_1_status = GPIO.input(PIR_PIN_1)
        if mailbox_1_status:
            time.sleep(0.1)  # Short wait to ensure signal stability
            if GPIO.input(PIR_PIN_1):  # Double check
                if mailbox_1_state != "Mail Detected":
                    mailbox_1_state = "Mail Detected"
                    log_mail("Mailbox 1")
                    socketio.emit('movement', {'sensor': 'Mailbox 1'})
        else:
            if mailbox_1_state != "No Mail":
                mailbox_1_state = "No Mail"
                socketio.emit('movement', {'sensor': 'Mailbox 1'})

        # Check Mailbox 2 sensor status
        mailbox_2_status = GPIO.input(PIR_PIN_2)
        if mailbox_2_status:
            time.sleep(0.1)  # Short wait to ensure signal stability
            if GPIO.input(PIR_PIN_2):  # Double check
                if mailbox_2_state != "Mail Detected":
                    mailbox_2_state = "Mail Detected"
                    log_mail("Mailbox 2")
                    socketio.emit('movement', {'sensor': 'Mailbox 2'})
        else:
            if mailbox_2_state != "No Mail":
                mailbox_2_state = "No Mail"
                socketio.emit('movement', {'sensor': 'Mailbox 2'})

        time.sleep(1)  # Check every second

def log_mail(sensor):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("INSERT INTO movements (sensor, timestamp) VALUES (?, ?)", 
              (sensor, datetime.datetime.now().replace(microsecond=0)))
    conn.commit()
    conn.close()

# Background thread to monitor mailboxes
threading.Thread(target=monitor_mailboxes, daemon=True).start()

def get_summary():
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()

    # Total movements
    c.execute("SELECT COUNT(*) FROM movements")
    total_movements = c.fetchone()[0]

    # Last 24 hours movements
    c.execute("SELECT COUNT(*) FROM movements WHERE timestamp >= datetime('now', '-1 day')")
    last_24_hours_movements = c.fetchone()[0]

    # Last week movements
    c.execute("SELECT COUNT(*) FROM movements WHERE timestamp >= datetime('now', '-7 
