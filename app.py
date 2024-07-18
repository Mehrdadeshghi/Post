from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

devices = []

@app.route('/')
def index():
    return render_template('index.html', devices=devices)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        data = request.form
        new_device = {
            "id": len(devices) + 1,
            "name": data['name'],
            "ip": data['ip'],
            "sensors": []
        }
        devices.append(new_device)
        return redirect(url_for('index'))
    return render_template('add_device.html')

@app.route('/devices')
def show_devices():
    return render_template('devices.html', devices=devices)

@app.route('/device/<int:device_id>')
def device_detail(device_id):
    device = next((d for d in devices if d["id"] == device_id), None)
    if device is None:
        return "Device not found", 404
    return render_template('device_detail.html', device=device)

@app.route('/device/<int:device_id>/add_sensor', methods=['POST'])
def add_sensor(device_id):
    device = next((d for d in devices if d["id"] == device_id), None)
    if device:
        data = request.json
        new_sensor = {
            "id": len(device['sensors']) + 1,
            "name": data['name']
        }
        device['sensors'].append(new_sensor)
        return jsonify(new_sensor)
    return jsonify({"error": "Device not found"}), 404

@app.route('/device/<int:device_id>/management')
def device_management(device_id):
    device = next((d for d in devices if d["id"] == device_id), None)
    if device is None:
        return "Device not found", 404
    return render_template('management.html', device=device)

@app.route('/device/<int:device_id>/user')
def device_user(device_id):
    device = next((d for d in devices if d["id"] == device_id), None)
    if device is None:
        return "Device not found", 404
    return render_template('user.html', device=device)

@app.route('/status')
def get_status():
    # Dummy status data
    status = {
        "message": "All systems operational",
        "last_update": "2024-07-18 12:00:00",
        "cpu_usage": 23,
        "memory_usage": 45,
        "disk_usage": 67,
        "cpu_temperature": 55,
        "system_uptime": "5 days, 4:32:10",
        "network_activity": {"upload": 10, "download": 20},
        "active_processes": 123
    }
    return jsonify(status)

@app.route('/system_info')
def system_info():
    # Dummy system info data
    system_info = {
        "cpu_usage": 23,
        "memory_usage": 45,
        "disk_usage": 67,
        "cpu_temperature": 55,
        "system_uptime": "5 days, 4:32:10",
        "network_activity": {"upload": 10, "download": 20},
        "active_processes": 123
    }
    return jsonify(system_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
