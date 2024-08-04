import psutil
import time
from influxdb import InfluxDBClient
import datetime
import socket
import requests

# InfluxDB-Verbindungsdetails
url = "http://45.149.78.188"
port = 8086
username = "myuser"
password = "mypassword"
database = "mydatabase"

client = InfluxDBClient(host=url, port=port, username=username, password=password, database=database)

# Funktion zur Abfrage der CPU-Temperatur (Linux)
def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = f.readline()
        return float(temp) / 1000.0
    except FileNotFoundError:
        return None

# Funktion zur Abfrage der öffentlichen IP-Adresse
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return None

# Funktion zur Abfrage des aktuellen Stromverbrauchs (Beispiel)
def get_power_consumption():
    try:
        with open('/sys/class/power_supply/energy_now', 'r') as f:
            power = f.readline()
        return float(power) / 1000000.0  # Umrechnung in Watt
    except FileNotFoundError:
        return None

# Initialwerte für die Netzwerkschnittstelle
net_io = psutil.net_io_counters()
prev_upload = net_io.bytes_sent
prev_download = net_io.bytes_recv

# Hostname und öffentliche IP-Adresse
hostname = socket.gethostname()
public_ip = get_public_ip()

while True:
    # CPU-Auslastung in Prozent
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # CPU-Temperatur in Grad Celsius
    cpu_temp = get_cpu_temp()
    
    # Gesamtspeicher und verwendeter Speicher in MB
    memory = psutil.virtual_memory()
    memory_total = memory.total / (1024 * 1024)
    memory_used = memory.used / (1024 * 1024)
    
    # Gesamter Speicher und verwendeter Speicher auf dem Dateisystem in GB
    disk = psutil.disk_usage('/')
    disk_total = disk.total / (1024 * 1024 * 1024)
    disk_used = disk.used / (1024 * 1024 * 1024)
    
    # Netzwerk-I/O
    net_io = psutil.net_io_counters()
    upload = net_io.bytes_sent
    download = net_io.bytes_recv
    
    upload_speed = (upload - prev_upload) / 1024.0  # KB/s
    download_speed = (download - prev_download) / 1024.0  # KB/s
    
    prev_upload = upload
    prev_download = download
    
    # System Uptime in Sekunden
    uptime_seconds = int(time.time() - psutil.boot_time())
    
    # Formatieren der Uptime für eine lesbare Ausgabe
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
    
    # Aktueller Stromverbrauch in Watt
    power_consumption = get_power_consumption()

    json_body = [
        {
            "measurement": "system",
            "tags": {
                "host": hostname,
                "public_ip": public_ip
            },
            "fields": {
                "cpu_usage": cpu_usage,
                "cpu_temp": cpu_temp,
                "memory_total": memory_total,
                "memory_used": memory_used,
                "disk_total": disk_total,
                "disk_used": disk_used,
                "upload_speed": upload_speed,
                "download_speed": download_speed,
                "total_upload": upload / (1024 * 1024),  # MB
                "total_download": download / (1024 * 1024),  # MB
                "uptime_seconds": uptime_seconds,
                "uptime_str": uptime_str,
                "power_consumption": power_consumption  # Watt
            }
        }
    ]

    try:
        client.write_points(json_body)
        print(f"Gesendete Systemdaten: {json_body}")
    except Exception as e:
        print(f"Fehler beim Senden der Daten an InfluxDB: {e}")
    
    time.sleep(10)  # Daten alle 10 Sekunden senden
