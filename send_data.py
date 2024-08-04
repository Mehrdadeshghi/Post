import psutil
import time
from influxdb import InfluxDBClient
import datetime
import socket
import requests
import subprocess

# InfluxDB-Verbindungsdetails
url = "http://45.149.78.188"
port = 8086
username = "myuser"
password = "mypassword"
database = "mydatabase"

client = InfluxDBClient(host=url, port=port, username=username, password=password, database=database)

# Funktion zur Abfrage der CPU-Temperatur (Raspberry Pi)
def get_cpu_temp():
    try:
        temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temp = float(temp.split("=")[1].split("'")[0])
        print(f"CPU Temp: {temp} °C")
        return temp
    except Exception as e:
        print(f"Failed to get CPU temperature: {e}")
        return None

# Funktion zur Abfrage der Spannung (Raspberry Pi)
def get_voltage():
    try:
        voltage = subprocess.check_output(["vcgencmd", "measure_volts"]).decode()
        voltage = float(voltage.split("=")[1].split("V")[0])
        print(f"Voltage: {voltage} V")
        return voltage
    except Exception as e:
        print(f"Failed to get voltage: {e}")
        return None

# Hostname und öffentliche IP-Adresse
hostname = socket.gethostname()
print(f"Hostname: {hostname}")

public_ip = None
try:
    response = requests.get('https://api.ipify.org')
    if response.status_code == 200:
        public_ip = response.text
    print(f"Public IP: {public_ip}")
except requests.RequestException:
    print("Failed to get public IP address.")

while True:
    # CPU-Temperatur in Grad Celsius
    cpu_temp = get_cpu_temp()
    
    # Aktuelle Spannung in Volt
    voltage = get_voltage()

    json_body = [
        {
            "measurement": "system",
            "tags": {
                "host": hostname,
                "public_ip": public_ip
            },
            "fields": {
                "cpu_temp": cpu_temp,
                "voltage": voltage  # Volt
            }
        }
    ]

    try:
        print(f"Sending data to InfluxDB: {json_body}")
        client.write_points(json_body)
        print("Data sent successfully")
    except Exception as e:
        print(f"Fehler beim Senden der Daten an InfluxDB: {e}")
    
    time.sleep(10)  # Daten alle 10 Sekunden senden
