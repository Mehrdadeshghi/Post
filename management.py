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
        cursor.execute("""
            SELECT rp.raspberry_id, rp.serial_number, rp.model, rp.os_version, rp.firmware_version, rp.ip_address, rp.created_at, l.street, l.house_number, l.postal_code, l.city, l.state, l.country
            FROM raspberry_pis rp
            LEFT JOIN mailboxes mb ON rp.mailbox_id = mb.mailbox_id
            LEFT JOIN locations l ON mb.location_id = l.location_id
        """)
        raspberry_pis = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(raspberry_pis), 200
    except Exception as e:
        print(f"Error: {e}")
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
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Abrufen der Infos eines Raspberry Pi
@app.route('/api/raspberry_pis/<int:raspberry_id>', methods=['GET'])
def get_raspberry_pi_info(raspberry_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rp.raspberry_id, rp.serial_number, rp.model, rp.os_version, rp.firmware_version, rp.ip_address, rp.created_at, mb.mailbox_id, l.street, l.house_number, l.postal_code, l.city, l.state, l.country
            FROM raspberry_pis rp
            LEFT JOIN mailboxes mb ON rp.mailbox_id = mb.mailbox_id
            LEFT JOIN locations l ON mb.location_id = l.location_id
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

        # Debugging-Ausgaben hinzufügen
        print(f"Received data: {data}")
        print(f"Raspberry ID: {raspberry_id}")

        if not all([street, house_number, postal_code, city, state, country]):
            print("Missing location fields")
            return jsonify({"error": "Missing location fields"}), 400

        conn = connect_db()
        cursor = conn.cursor()

        # Debugging-Ausgaben hinzufügen
        print(f"Updating location for Raspberry Pi {raspberry_id} with data: {data}")

        cursor.execute("""
            UPDATE locations
            SET street = %s, house_number = %s, postal_code = %s, city = %s, state = %s, country = %s
            FROM mailboxes mb
            WHERE mb.mailbox_id = (
                SELECT mailbox_id FROM raspberry_pis WHERE raspberry_id = %s
            ) AND locations.location_id = mb.location_id
        """, (street, house_number, postal_code, city, state, country, raspberry_id))
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Successfully updated location for Raspberry Pi {raspberry_id}")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# HTML-Seite rendern
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
