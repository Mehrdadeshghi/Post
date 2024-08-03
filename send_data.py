import requests
import json
from datetime import datetime

# API Key und Server-URL
API_KEY = 'Ihr_API_Schlüssel'
SERVER_URL = 'http://45.149.78.188/api/datasources/proxy/1/push'

# Beispiel-Daten
data = {
    "streams": [
        {
            "labels": "{job=\"raspberry_pi\"}",
            "entries": [
                {
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "line": "temperature=30.5"
                }
            ]
        }
    ]
}

# Header für die API-Anfrage
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

# Daten an den Server senden
response = requests.post(SERVER_URL, headers=headers, data=json.dumps(data))

# Ergebnis überprüfen
if response.status_code == 204:
    print("Daten erfolgreich gesendet")
else:
    print(f"Fehler beim Senden der Daten: {response.status_code}, {response.text}")
