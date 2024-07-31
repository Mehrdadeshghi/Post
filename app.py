from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import RPi.GPIO as GPIO
import time
import threading
import sqlite3
import datetime
import psutil
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensors.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Create the database and the User table if they don't exist
db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    controllers = [{"ip": "192.168.178.82", "name": "Controller 1"}]
    return render_template('index.html', controllers=controllers)

@app.route('/controller/<ip>')
@login_required
def controller(ip):
    sensors = [{"name": "Mehrdad", "pin": 25}, {"name": "Rezvaneh", "pin": 23}]
    return render_template('controller.html', sensors=sensors, controller_ip=ip)

@app.route('/sensor/<sensor_name>')
@login_required
def sensor(sensor_name):
    data = get_aggregated_data(sensor_name)
    return render_template('sensor.html', sensor_name=sensor_name, data=data)

@app.route('/api/movements/<sensor_name>')
@login_required
def api_movements(sensor_name):
    data = get_aggregated_data(sensor_name)
    return jsonify(data)

@app.route('/api/system_info')
@login_required
def api_system_info():
    data = get_system_info()
    return jsonify(data)

@app.route('/system_info/<ip>')
@login_required
def system_info(ip):
    data = get_system_info()
    return render_template('system_info.html', controller_ip=ip, data=data)

def monitor_mailboxes():
    global mailbox_1_state, mailbox_2_state
    while True:
        # Check Mehrdad sensor status
        mehrdad_status = GPIO.input(PIR_PIN_1)
        if mehrdad_status:
            time.sleep(0.1)  # Kurzes Warten, um sicherzustellen, dass das Signal stabil ist
            if GPIO.input(PIR_PIN_1):  # Doppelt überprüfen
                if mailbox_1_state != "Mail Detected":
                    mailbox_1_state = "Mail Detected"
                    log_mail("Mehrdad")
                    socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'Mail Detected'})
        else:
            if mailbox_1_state != "No Mail":
                mailbox_1_state = "No Mail"
                socketio.emit('movement', {'sensor': 'Mehrdad', 'status': 'No Mail'})

        # Check Rezvaneh sensor status
        rezvaneh_status = GPIO.input(PIR_PIN_2)
        if rezvaneh_status:
            time.sleep(0.1)  # Kurzes Warten, um sicherzustellen, dass das Signal stabil ist
            if GPIO.input(PIR_PIN_2):  # Doppelt überprüfen
                if mailbox_2_state != "Mail Detected":
                    mailbox_2_state = "Mail Detected"
                    log_mail("Rezvaneh")
                    socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'Mail Detected'})
        else:
            if mailbox_2_state != "No Mail":
                mailbox_2_state = "No Mail"
                socketio.emit('movement', {'sensor': 'Rezvaneh', 'status': 'No Mail'})

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

def get_aggregated_data(sensor_name):
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()

    # Total movements
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=?", (sensor_name,))
    total_movements = c.fetchone()[0]

    # Last 24 hours
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=? AND timestamp >= datetime('now', '-1 day')", (sensor_name,))
    last_24h_movements = c.fetchone()[0]

    # Last week
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=? AND timestamp >= datetime('now', '-7 days')", (sensor_name,))
    last_week_movements = c.fetchone()[0]

    # Last month
    c.execute("SELECT COUNT(*) FROM movements WHERE sensor=? AND timestamp >= datetime('now', '-1 month')", (sensor_name,))
    last_month_movements = c.fetchone()[0]

    # Last movement
    c.execute("SELECT timestamp FROM movements WHERE sensor=? ORDER BY timestamp DESC LIMIT 1", (sensor_name,))
    last_movement = c.fetchone()
    last_movement = last_movement[0] if last_movement else None

    # Last 10 movements
    c.execute("SELECT timestamp FROM movements WHERE sensor=? ORDER BY timestamp DESC LIMIT 10", (sensor_name,))
    last_10_movements = c.fetchall()

    # All movements for the graph
    c.execute("SELECT timestamp FROM movements WHERE sensor=?", (sensor_name,))
    all_movements = c.fetchall()

    conn.close()

    return {
        "total_movements": total_movements,
        "last_24h_movements": last_24h_movements,
        "last_week_movements": last_week_movements,
        "last_month_movements": last_month_movements,
        "last_movement": last_movement,
        "last_10_movements": last_10_movements,
        "all_movements": all_movements
    }

def get_system_info():
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    cpu_temps = psutil.sensors_temperatures()
    cpu_temp = cpu_temps.get('cpu-thermal', cpu_temps.get('coretemp', [{'current': None}]))[0]['current']
    net_io = psutil.net_io_counters()
    return {
        "system_name": "Raspberry Pi",
        "system_ip": "192.168.178.82",
        "system_uptime": str(uptime),
        "cpu_temp": cpu_temp,
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "network_upload": net_io.bytes_sent,
        "network_download": net_io.bytes_recv,
        "active_processes": len(psutil.pids())
    }

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
