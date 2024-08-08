from flask import Flask, request, render_template, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Datenbankverbindung einrichten
def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

# API-Endpunkt zum Abrufen aller Raspberry Pis
@app.route('/api/raspberry_pis', methods=['GET'])
def get_raspberry_pis():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT raspberry_id, serial_number, model, os_version, firmware_version, location FROM raspberry_pis")
        raspberry_pis = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(raspberry_pis), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Abrufen der PIR-Sensoren eines Raspberry Pi
@app.route('/api/raspberry_pis/<int:raspberry_id>/sensors', methods=['GET'])
def get_pir_sensors(raspberry_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT sensor_id, location FROM pir_sensors WHERE raspberry_id = %s", (raspberry_id,))
        sensors = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Abrufen der Infos eines Raspberry Pi
@app.route('/api/raspberry_pis/<int:raspberry_id>', methods=['GET'])
def get_raspberry_pi_info(raspberry_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT raspberry_id, serial_number, model, os_version, firmware_version, location FROM raspberry_pis WHERE raspberry_id = %s", (raspberry_id,))
        raspberry_pi = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(raspberry_pi), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Aktualisieren der Standortinformationen eines Raspberry Pi
@app.route('/api/raspberry_pis/<int:raspberry_id>', methods=['POST'])
def update_raspberry_pi_location(raspberry_id):
    try:
        data = request.json
        location = data.get('location')

        if not location:
            return jsonify({"error": "Missing location"}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE raspberry_pis SET location = %s WHERE raspberry_id = %s", (location, raspberry_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# HTML-Seite rendern
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
