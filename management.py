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

# HTML-Seite rendern
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
