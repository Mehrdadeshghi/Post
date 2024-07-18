from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

devices = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_device', methods=['POST'])
def add_device():
    data = request.json
    new_device = {
        "id": len(devices) + 1,
        "name": data['name'],
        "ip": data['ip'],
        "sensors": []
    }
    devices.append(new_device)
    return jsonify(new_device)

@app.route('/add_sensor', methods=['POST'])
def add_sensor():
    data = request.json
    device_id = data['device_id']
    sensor_name = data['name']
    for device in devices:
        if device['id'] == device_id:
            new_sensor = {
                "id": len(device['sensors']) + 1,
                "name": sensor_name
            }
            device['sensors'].append(new_sensor)
            return jsonify(new_sensor)
    return jsonify({"error": "Device not found"}), 404

@app.route('/devices')
def get_devices():
    return jsonify(devices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
