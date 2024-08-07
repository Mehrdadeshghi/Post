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

        # Verbindung zur Datenbank
        conn = connect_db()
        cursor = conn.cursor()

        # SQL-Abfrage zum Einfügen der PIR-Daten
        cursor.execute("""
            INSERT INTO sensor_data (sensor_id, timestamp, movement_detected)
            VALUES (%s, %s, %s);
        """, (sensor_id, datetime.now(), movement_detected))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
