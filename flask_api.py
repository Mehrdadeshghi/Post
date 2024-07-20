from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

bewegungen = []

@app.route('/bewegung', methods=['POST'])
def erfassen_bewegung():
    daten = request.get_json()
    if 'sensor' in daten and 'zeit' in daten:
        bewegungen.append(daten)
        print(f"Erfasste Bewegung: {daten}")  # Debug-Ausgabe
    return jsonify({"status": "erfasst"}), 200

@app.route('/bewegungen', methods=['GET'])
def anzeigen_bewegungen():
    return jsonify(bewegungen), 200

@app.route('/')
def index():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
