from flask import Flask, jsonify, render_template, send_file, request
import pandas as pd
import io
from datetime import datetime, timedelta
from threading import Thread
import psutil
from gpio_handling import GPIOHandler
from system_info import get_system_info
from sensor_handling import StateMachine, SensorHandler

app = Flask(__name__)
app.config['DEBUG'] = True  # Activate debug mode

# Define GPIO pins
SENSOR_PINS = {25: "Mehrdad", 24: "Rezvaneh"}  # Pins for the motion sensors

# Initialize GPIO handler
gpio_handler = GPIOHandler(SENSOR_PINS)

# Initialize state machine and sensor handler
state_machine = StateMachine()
sensor_handler = SensorHandler(gpio_handler, state_machine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/controller/<controller_name>')
def controller(controller_name):
    sensors = [{"gpio": pin, "name": name} for pin, name in SENSOR_PINS.items()]
    return render_template('controller.html', controller_name=controller_name, sensors=sensors)

@app.route('/sensor/<sensor_name>')
def sensor(sensor_name):
    for pin, name in SENSOR_PINS.items():
        if sensor_name.lower() == name.lower():
            return render_template('user.html', sensor_name=sensor_name, sensor_pin=pin)
    return "Sensor not found", 404

@app.route('/sensor_status')
def sensor_status():
    sensor_statuses = {name: gpio_handler.get_sensor_input(pin) for pin, name in SENSOR_PINS.items()}
    return jsonify(sensor_statuses)

@app.route('/system_info')
def system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    disk_usage = psutil.disk_usage('/').percent
    cpu_temperature, uptime, upload, download, active_processes = get_system_info()
    print(f"Fetched system info - CPU Temp: {cpu_temperature}, Uptime: {uptime}, Upload: {upload}, Download: {download}, Active Processes: {active_processes}")
    sensor_handler.status.update({
        "cpu_temperature": cpu_temperature,
        "system_uptime": uptime,
        "network_activity": {"upload": upload, "download": download},
        "active_processes": active_processes
    })
    return jsonify({
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "cpu_temperature": cpu_temperature,
        "system_uptime": uptime,
        "network_activity": {"upload": upload, "download": download},
        "active_processes": active_processes
    })

@app.route('/status')
def get_status():
    return jsonify(sensor_handler.status)

@app.route('/movements')
def get_movements():
    sensor_pin = request.args.get('sensor_pin', type=int)
    if sensor_pin in sensor_handler.status["movements"]:
        return jsonify(sensor_handler.status["movements"][sensor_pin])
    return jsonify([])

@app.route('/summary')
def get_summary():
    summaries = {}
    now = datetime.now()
    for pin, movements in sensor_handler.status["movements"].items():
        last_24_hours_movements = [m for m in movements if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(hours=24)]
        last_week_movements = [m for m in movements if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(weeks=1)]
        last_month_movements = [m for m in movements if datetime.strptime(m, "%Y-%m-%d %H:%M:%S") > now - timedelta(days=30)]
        summaries[pin] = {
            "total_movements": len(movements),
            "last_24_hours_movements": len(last_24_hours_movements),
            "last_week_movements": len(last_week_movements),
            "last_month_movements": len(last_month_movements),
            "last_motion_time": movements[-1] if movements else "No movements detected"
        }
    return jsonify(summaries)

@app.route('/hourly_movements')
def get_hourly_movements():
    sensor_pin = request.args.get('sensor_pin', type=int)
    if sensor_pin in sensor_handler.status["movements"]:
        now = datetime.now()
        hourly_movements = {str(hour): 0 for hour in range(24)}
        for movement in sensor_handler.status["movements"][sensor_pin]:
            movement_time = datetime.strptime(movement, "%Y-%m-%d %H:%M:%S")
            if movement_time.date() == now.date():
                hour = movement_time.hour
                hourly_movements[str(hour)] += 1
        return jsonify(hourly_movements)
    return jsonify({})

@app.route('/download/csv')
def download_csv():
    sensor_pin = request.args.get('sensor_pin', type=int)
    if sensor_pin in sensor_handler.status["movements"]:
        df = pd.DataFrame(sensor_handler.status["movements"][sensor_pin], columns=["Time"])
        output = io.BytesIO()
        df.to_csv(output, index_label="Index")
        output.seek(0)
        return send_file(output, mimetype='text/csv', download_name='movements.csv', as_attachment=True)
    return "No data", 404

@app.route('/download/excel')
def download_excel():
    sensor_pin = request.args.get('sensor_pin', type=int)
    if sensor_pin in sensor_handler.status["movements"]:
        df = pd.DataFrame(sensor_handler.status["movements"][sensor_pin], columns=["Time"])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index_label="Index")
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='movements.xlsx', as_attachment=True)
    return "No data", 404

@app.route('/download/system_info/csv')
def download_system_info_csv():
    system_info = {
        "CPU Temperature": [sensor_handler.status["cpu_temperature"]],
        "System Uptime": [sensor_handler.status["system_uptime"]],
        "Upload": [sensor_handler.status["network_activity"]["upload"]],
        "Download": [sensor_handler.status["network_activity"]["download"]],
        "Active Processes": [sensor_handler.status["active_processes"]]
    }
    df = pd.DataFrame(system_info)
    output = io.BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='system_info.csv', as_attachment=True)

@app.route('/download/system_info/excel')
def download_system_info_excel():
    system_info = {
        "CPU Temperature": [sensor_handler.status["cpu_temperature"]],
        "System Uptime": [sensor_handler.status["system_uptime"]],
        "Upload": [sensor_handler.status["network_activity"]["upload"]],
        "Download": [sensor_handler.status["network_activity"]["download"]],
        "Active Processes": [sensor_handler.status["active_processes"]]
    }
    df = pd.DataFrame(system_info)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='system_info.xlsx', as_attachment=True)

if __name__ == '__main__':
    try:
        sensor_thread = Thread(target=sensor_handler.check_sensor)
        sensor_thread.start()
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        gpio_handler.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        gpio_handler.cleanup()
