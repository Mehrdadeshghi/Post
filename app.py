from flask import Flask
from sensor import sensor_bp
from management import management_bp

app = Flask(__name__)

# Registrierung der Blueprints mit ihren URL-Präfixen
app.register_blueprint(sensor_bp, url_prefix='/sensor')
app.register_blueprint(management_bp, url_prefix='/management')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
