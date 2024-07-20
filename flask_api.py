from flask import Flask, request, jsonify

app = Flask(__name__)

bewegungen = []

@app.route('/bewegung', methods=['POST'])
def erfassen_bewegung():
    daten = request.get_json()
    bewegungen.append(daten)
    return jsonify({"status": "erfasst"}), 200

@app.route('/bewegungen', methods=['GET'])
def anzeigen_bewegungen():
    return jsonify(bewegungen), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
