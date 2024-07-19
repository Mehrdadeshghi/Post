import sqlite3
import nmap
from flask import Flask, request, render_template, redirect, g, jsonify
import os
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

DATABASE = 'database.db'

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pins = list(range(2, 28))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_first_request
def create_tables():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def check_pin(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin) == GPIO.HIGH

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pin_states')
def pin_states():
    states = {pin: check_pin(pin) for pin in pins}
    return jsonify(states)

@app.route('/api/add_device', methods=['POST'])
def add_device():
    data = request.json
    pin = data['pin']
    name = data['name']
    if not pin or not name:
        return jsonify({'error': 'Missing data'}), 400
    conn = get_db()
    existing_device = conn.execute('SELECT * FROM Devices WHERE pin = ?', (pin,)).fetchone()
    if existing_device:
        return jsonify({'error': 'Device already exists on this pin'}), 409
    conn.execute('INSERT INTO Devices (pin, name) VALUES (?, ?)', (pin, name))
    conn.commit()
    conn.close()
    return jsonify({'success': 'Device added', 'pin': pin, 'name': name}), 201

def scan_ports(hostname):
    nm = nmap.PortScanner()
    try:
        nm.scan(hostname, '1-1024')  # Scan Ports 1-1024
        if hostname not in nm.all_hosts():
            print(f"Host {hostname} not found in scan results.")
            return []
        
        ports = []
        for proto in nm[hostname].all_protocols():
            lport = nm[hostname][proto].keys()
            for port in lport:
                state = nm[hostname][proto][port]['state']
                ports.append((hostname, port, state))
        return ports
    except Exception as e:
        print(f"An error occurred while scanning {hostname}: {e}")
        return []

@app.route('/add_building', methods=('GET', 'POST'))
def add_building():
    if request.method == 'POST':
        city = request.form['city']
        postal_code = request.form['postal_code']
        street = request.form['street']
        house_number = request.form['house_number']
        hostname = request.form['hostname']
        
        conn = get_db()
        conn.execute('INSERT INTO Buildings (city, postal_code, street, house_number, hostname) VALUES (?, ?, ?, ?, ?)',
                     (city, postal_code, street, house_number, hostname))
        conn.commit()
        
        ports = scan_ports(hostname)
        for hostname, port, state in ports:
            conn.execute('INSERT INTO Ports (hostname, port, state) VALUES (?, ?, ?)', (hostname, port, state))
        
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add_building.html')

@app.route('/add_pir_sensor', methods=('GET', 'POST'))
def add_pir_sensor():
    conn = get_db()
    rps = conn.execute('SELECT hostname FROM Buildings').fetchall()
    conn.close()

    if request.method == 'POST':
        rp_hostname = request.form['rp_hostname']
        sensor_number = request.form['sensor_number']
        postbox_number = request.form['postbox_number']
        port = request.form['port']
        
        conn = get_db()
        conn.execute('INSERT INTO PIR_Sensors (rp_hostname, sensor_number, postbox_number, port) VALUES (?, ?, ?, ?)',
                     (rp_hostname, sensor_number, postbox_number, port))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add_pir_sensor.html', rps=rps)

@app.route('/get_ports/<hostname>', methods=['GET'])
def get_ports(hostname):
    conn = get_db()
    ports = conn.execute('SELECT port FROM Ports WHERE hostname = ?', (hostname,)).fetchall()
    conn.close()
    return jsonify([port['port'] for port in ports])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
