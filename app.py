from flask import Flask
from config import Config
from auth_module import auth_bp
from management import management_bp
from user import user_bp

app = Flask(__name__)
app.config.from_object(Config)

# Registriere die Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(management_bp, url_prefix='/management')
app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

