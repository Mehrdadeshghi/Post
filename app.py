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
    c.execute("SELECT COUNT(*) FROM movements WHERE timestamp >= datetime('now', '-7 days')")
    last_week_movements = c.fetchone()[0]

    # Last month movements
    c.execute("SELECT COUNT(*) FROM movements WHERE timestamp >= datetime('now', '-1 month')")
    last_month_movements = c.fetchone()[0]

    # Last motion time
    c.execute("SELECT timestamp FROM movements ORDER BY timestamp DESC LIMIT 1")
    last_motion_time = c.fetchone()
    last_motion_time = last_motion_time[0] if last_motion_time else "No movements detected"

    conn.close()

    return {
        "total_movements": total_movements,
        "last_24_hours_movements": last_24_hours_movements,
        "last_week_movements": last_week_movements,
        "last_month_movements": last_month_movements,
        "last_motion_time": last_motion_time
    }

def get_last_10_movements():
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("SELECT timestamp FROM movements ORDER BY timestamp DESC LIMIT 10")
    last_10_movements = c.fetchall()
    conn.close()
    return [movement[0] for movement in last_10_movements]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/summary')
def summary():
    return jsonify(get_summary())

@app.route('/movements')
def movements():
    return jsonify(get_last_10_movements())

@app.route('/hourly_movements')
def hourly_movements():
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("SELECT strftime('%H', timestamp) as hour, COUNT(*) FROM movements GROUP BY hour")
    hourly_movements = dict(c.fetchall())
    conn.close()
    return jsonify(hourly_movements)

@app.route('/download/csv')
def download_csv():
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute("SELECT * FROM movements")
    data = c.fetchall()
    conn.close()
    with open('movements.csv', 'w') as f:
        f.write('id,sensor,timestamp\n')
        for row in data:
            f.write(','.join(map(str, row)) + '\n')
    return send_file('movements.csv', as_attachment=True)

@app.route('/download/excel')
def download_excel():
    # Implement Excel file creation logic
    pass

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
