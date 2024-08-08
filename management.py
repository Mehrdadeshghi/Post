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

# API-Endpunkt zum Abrufen der Raspberry Pi ID anhand der Seriennummer
@app.route('/get_raspberry_id', methods=['GET'])
def get_raspberry_id():
    serial_number = request.args.get('serial_number')
    if not serial_number:
        return jsonify({"error": "Missing serial_number"}), 400
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT raspberry_id FROM raspberry_pis WHERE serial_number = %s", (serial_number,))
        raspberry_pi = cursor.fetchone()
        cursor.close()
        conn.close()
        if raspberry_pi:
            return jsonify({"raspberry_id": raspberry_pi[0]}), 200
        else:
            return jsonify({"error": "Serial number not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Registrieren eines neuen Raspberry Pi
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        serial_number = data.get('serial_number')
        model = data.get('model')
        os_version = data.get('os_version')
        firmware_version = data.get('firmware_version')
        ip_address = data.get('ip_address')

        if not all([serial_number, model, os_version, firmware_version, ip_address]):
            return jsonify({"error": "Missing fields"}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO raspberry_pis (serial_number, model, os_version, firmware_version, ip_address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING raspberry_id;
        """, (serial_number, model, os_version, firmware_version, ip_address, datetime.now()))
        raspberry_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"raspberry_id": raspberry_id}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
