from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True

# Datenbankverbindung einrichten
def connect_db():
    return psycopg2.connect(
        dbname="deine_datenbank",
        user="dein_benutzer",
        password="dein_passwort",
        host="localhost"
    )

# API-Endpunkt für die Registrierung
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        serial_number = data.get('serial_number')
        model = data.get('model')
        os_version = data.get('os_version')
        firmware_version = data.get('firmware_version')
        ip_address = data.get('ip_address')

        if not all([serial_number, model, os_version, firmware_version, ip_address]):
            return jsonify({"error": "Missing fields"}), 400

        # Verbindung zur Datenbank
        conn = connect_db()
        cursor = conn.cursor()

        # SQL-Abfrage zum Einfügen der Daten
        cursor.execute("""
            INSERT INTO raspberry_pis (serial_number, model, os_version, firmware_version, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING raspberry_id;
        """, (serial_number, model, os_version, firmware_version, datetime.now()))

        raspberry_id = cursor.fetchone()[0]
        conn.commit()

        cursor.execute("""
            INSERT INTO raspberry_logs (raspberry_id, timestamp, status, public_ip)
            VALUES (%s, %s, %s, %s);
        """, (raspberry_id, datetime.now(), 'Registered', ip_address))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "raspberry_id": raspberry_id}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
