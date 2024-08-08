from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True

# Datenbankverbindung einrichten
def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

# API-Endpunkt für das Hinzufügen von Sensoren
@app.route('/add_sensor', methods=['POST'])
def add_sensor():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        raspberry_id = data.get('raspberry_id')
        location = data.get('location')

        if not raspberry_id or not location:
            return jsonify({"error": "Missing fields"}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pir_sensors (raspberry_id, location, created_at)
            VALUES (%s, %s, %s)
            RETURNING sensor_id;
        """, (raspberry_id, location, datetime.now()))
        sensor_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"sensor_id": sensor_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API-Endpunkt für das Speichern der PIR-Daten
@app.route('/pir_data', methods=['POST'])
def save_pir_data():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        sensor_id = data.get('sensor_id')
        movement_detected = data.get('movement_detected')

        if sensor_id is None or movement_detected is None:
            return jsonify({"error": "Missing fields"}), 400

        if not isinstance(sensor_id, int):
            return jsonify({"error": "Invalid sensor_id type"}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_data (sensor_id, timestamp, movement_detected)
            VALUES (%s, %s, %s);
        """, (sensor_id, datetime.now(), movement_detected))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
