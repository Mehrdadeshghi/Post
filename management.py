from flask import Flask, request, render_template, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT rp.raspberry_id, rp.serial_number, rp.model, rp.os_version, rp.firmware_version, rp.ip_address, rp.created_at, l.street, l.house_number, l.postal_code, l.city, l.state, l.country
            FROM raspberry_pis rp
            LEFT JOIN locations l ON rp.location_id = l.location_id
        """)
        raspberry_pis = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(raspberry_pis), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Abrufen der Infos eines Raspberry Pi
@app.route('/api/raspberry_pis/<int:raspberry_id>', methods=['GET'])
def get_raspberry_pi_info(raspberry_id):
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT rp.raspberry_id, rp.serial_number, rp.model, rp.os_version, rp.firmware_version, rp.ip_address, rp.created_at, l.street, l.house_number, l.postal_code, l.city, l.state, l.country
            FROM raspberry_pis rp
            LEFT JOIN locations l ON rp.location_id = l.location_id
            WHERE rp.raspberry_id = %s
        """, (raspberry_id,))
        raspberry_pi = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(raspberry_pi), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Aktualisieren der Standortinformationen eines Raspberry Pi
@app.route('/api/raspberry_pis/<int:raspberry_id>/location', methods=['POST'])
def update_raspberry_pi_location(raspberry_id):
    try:
        data = request.json
        street = data.get('street')
        house_number = data.get('house_number')
        postal_code = data.get('postal_code')
        city = data.get('city')
        state = data.get('state')
        country = data.get('country')

        if not all([street, house_number, postal_code, city, state, country]):
            return jsonify({"error": "Missing location fields"}), 400

        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Überprüfen, ob der Standort bereits existiert
        cursor.execute("""
            SELECT location_id FROM locations
            WHERE street = %s AND house_number = %s AND postal_code = %s AND city = %s AND state = %s AND country = %s
        """, (street, house_number, postal_code, city, state, country))
        location = cursor.fetchone()

        if location:
            location_id = location['location_id']
        else:
            cursor.execute("""
                INSERT INTO locations (street, house_number, postal_code, city, state, country)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING location_id
            """, (street, house_number, postal_code, city, state, country))
            location_id = cursor.fetchone()['location_id']

        cursor.execute("""
            UPDATE raspberry_pis
            SET location_id = %s
            WHERE raspberry_id = %s
        """, (location_id, raspberry_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Abrufen der PIR-Sensoren eines Raspberry Pi
@app.route('/api/raspberry_pis/<int:raspberry_id>/sensors', methods=['GET'])
def get_pir_sensors(raspberry_id):
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT sensor_id, location FROM pir_sensors WHERE raspberry_id = %s", (raspberry_id,))
        sensors = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(sensors), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Seite zum Zuweisen des Standorts anzeigen
@app.route('/assign_location/<int:raspberry_id>')
def assign_location(raspberry_id):
    return render_template('assign_location.html', raspberry_id=raspberry_id)

# HTML-Seite rendern
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
