from flask import request, jsonify
from . import management_bp
import psycopg2
from psycopg2.extras import RealDictCursor

def connect_db():
    return psycopg2.connect(
        dbname="deine_datenbank",
        user="dein_benutzer",
        password="dein_passwort",
        host="localhost"
    )

@management_bp.route('/register', methods=['POST'])
def register_raspberry_pi():
    data = request.json
    serial_number = data.get('serial_number')
    model = data.get('model')
    os_version = data.get('os_version')
    firmware_version = data.get('firmware_version')
    ip_address = data.get('ip_address')
    
    if not serial_number:
        return jsonify({"error": "Serial number is required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Prüfen, ob der Raspberry Pi bereits registriert ist
        cursor.execute("SELECT * FROM raspberry_pis WHERE serial_number = %s", (serial_number,))
        raspberry_pi = cursor.fetchone()

        if raspberry_pi:
            cursor.close()
            conn.close()
            return jsonify({"raspberry_id": raspberry_pi['raspberry_id']}), 200
        
        # Neuen Raspberry Pi registrieren
        cursor.execute("""
            INSERT INTO raspberry_pis (serial_number, model, os_version, firmware_version, ip_address)
            VALUES (%s, %s, %s, %s, %s) RETURNING raspberry_id
        """, (serial_number, model, os_version, firmware_version, ip_address))
        raspberry_id = cursor.fetchone()['raspberry_id']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"raspberry_id": raspberry_id}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/get_raspberry_id', methods=['GET'])
def get_raspberry_id():
    serial_number = request.args.get('serial_number')
    
    if not serial_number:
        return jsonify({"error": "Serial number is required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT raspberry_id FROM raspberry_pis WHERE serial_number = %s", (serial_number,))
        raspberry_pi = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if raspberry_pi:
            return jsonify({"raspberry_id": raspberry_pi['raspberry_id']}), 200
        else:
            return jsonify({"error": "Serial number not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/add_sensor', methods=['POST'])
def add_sensor():
    data = request.json
    raspberry_id = data.get('raspberry_id')
    location = data.get('location')

    if not raspberry_id or not location:
        return jsonify({"error": "Raspberry ID and location are required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO pir_sensors (raspberry_id, location)
            VALUES (%s, %s) RETURNING sensor_id
        """, (raspberry_id, location))
        sensor_id = cursor.fetchone()['sensor_id']

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"sensor_id": sensor_id}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/check_sensor', methods=['GET'])
def check_sensor():
    raspberry_id = request.args.get('raspberry_id')
    location = request.args.get('location')

    if not raspberry_id or not location:
        return jsonify({"error": "Raspberry ID and location are required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT sensor_id FROM pir_sensors WHERE raspberry_id = %s AND location = %s
        """, (raspberry_id, location))
        sensor = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if sensor:
            return jsonify({"sensor_id": sensor['sensor_id']}), 200
        else:
            return jsonify({"error": "Sensor not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/pir_data', methods=['POST'])
def receive_pir_data():
    data = request.json
    sensor_id = data.get('sensor_id')
    movement_detected = data.get('movement_detected')

    if not sensor_id or movement_detected is None:
        return jsonify({"error": "Sensor ID and movement detected status are required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sensor_data (sensor_id, movement_detected)
            VALUES (%s, %s)
        """, (sensor_id, movement_detected))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Data received successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
