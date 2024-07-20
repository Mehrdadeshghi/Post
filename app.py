from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

motion_data = []

@app.route('/motion', methods=['POST'])
def log_motion():
    data = request.json
    motion_data.append(data)
    return 'Bewegung erfasst', 200

@app.route('/motion', methods=['GET'])
def get_motion():
    return jsonify(motion_data), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
