import sqlite3
import nmap
from flask import Flask, request, render_template, redirect, g, jsonify
import os

app = Flask(__name__)

DATABASE = 'database.db'

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

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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

@app.route('/')
def index():
    conn = get_db()
    buildings = conn.execute('SELECT * FROM Buildings').fetchall()
    conn.close()
    return render_template('index.html', buildings=buildings)

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
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
