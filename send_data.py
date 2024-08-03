from influxdb import InfluxDBClient
import random
import time

# Details für den InfluxDB-Server
url = "45.149.78.188"
port = 8086
username = "myuser"
password = "mypassword"
database = "mydatabase"

client = InfluxDBClient(url, port, username, password, database)

while True:
    # Simulierte Sensordaten
    temperature = random.uniform(20.0, 25.0)
    humidity = random.uniform(30.0, 50.0)

    json_body = [
        {
            "measurement": "environment",
            "tags": {
                "location": "RaspberryPi"
            },
            "fields": {
                "temperature": temperature,
                "humidity": humidity
            }
        }
    ]

    client.write_points(json_body)
    print(f"Gesendete Daten: Temperatur={temperature}, Feuchtigkeit={humidity}")
    
    time.sleep(10)  # Daten alle 10 Sekunden senden
