from flask import Flask
from sensor import sensor_bp
from management import management_bp

app = Flask(__name__)
app.register_blueprint(sensor_bp, url_prefix='/sensor')
app.register_blueprint(management_bp, url_prefix='/management')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
