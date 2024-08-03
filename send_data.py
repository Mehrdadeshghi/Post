import psutil
import time
import netifaces as ni
from influxdb import InfluxDBClient

# InfluxDB-Verbindungsdetails
url = "45.149.78.188"
port = 8086
username = "myuser"
password = "mypassword"
database = "mydatabase"

client = InfluxDBClient(url, port, username, password, database)

# Funktion zur Abfrage der CPU-Temperatur (Linux)
def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = f.readline()
        return float(temp) / 1000.0
    except FileNotFoundError:
        return None

# Funktion zur Abfrage der Netzwerkschnittstelle
def get_network_interface():
    interfaces = ni.interfaces()
    for iface in interfaces:
        if iface != 'lo':
            return iface
    return None

# Initialwerte für die Netzwerkschnittstelle
interface = get_network_interface()
net_io = psutil.net_io_counters(pernic=True)
prev_upload = net_io[interface].bytes_sent
prev_download = net_io[interface].bytes_recv

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
    net_io = psutil.net_io_counters(pernic=True)
    upload = net_io[interface].bytes_sent
    download = net_io[interface].bytes_recv
    
    upload_speed = (upload - prev_upload) / 1024.0  # KB/s
    download_speed = (download - prev_download) / 1024.0  # KB/s
    
    prev_upload = upload
    prev_download = download

    json_body = [
        {
            "measurement": "system",
            "tags": {
                "host": "RaspberryPi"
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
                "total_download": download / (1024 * 1024)  # MB
            }
        }
    ]

    client.write_points(json_body)
    print(f"Gesendete Systemdaten: {json_body}")
    time.sleep(10)  # Daten alle 10 Sekunden senden
