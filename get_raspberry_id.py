from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Datenbankverbindung einrichten
def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

# API-Endpunkt zum Abrufen der raspberry_id anhand der Seriennummer
@app.route('/get_raspberry_id', methods=['GET'])
def get_raspberry_id():
    serial_number = request.args.get('serial_number')
    if not serial_number:
        return jsonify({"error": "No serial_number provided"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT raspberry_id FROM raspberry_pis WHERE serial_number = %s", (serial_number,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return jsonify({"raspberry_id": result[0]}), 200
        else:
            return jsonify({"error": "Serial number not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
