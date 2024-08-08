from flask import Flask, render_template, jsonify
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

# API-Endpunkt zum Abrufen der PIR-Sensordaten
@app.route('/api/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100")
        sensor_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(sensor_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# HTML-Seite dienen
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
