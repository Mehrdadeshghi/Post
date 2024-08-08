import os

class Config:
    SECRET_KEY = os.urandom(24)
    # Weitere Konfigurationen wie Datenbank-URL etc.
