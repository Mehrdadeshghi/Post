from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import time

# Details für den InfluxDB-Server
url = "http://45.149.78.188:8086"
username = "myuser"
password = "mypassword"
bucket = "mydatabase"

# Erstellen der Verbindung
client = InfluxDBClient(url=url, username=username, password=password, org="")

# API für das Schreiben von Daten
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    # Simulierte Sensordaten
    temperature = random.uniform(20.0, 25.0)
    humidity = random.uniform(30.0, 50.0)

    point = Point("environment") \
        .tag("location", "RaspberryPi") \
        .field("temperature", temperature) \
        .field("humidity", humidity)

    write_api.write(bucket=bucket, org="", record=point)
    print(f"Gesendete Daten: Temperatur={temperature}, Feuchtigkeit={humidity}")
    
    time.sleep(10)  # Daten alle 10 Sekunden senden
