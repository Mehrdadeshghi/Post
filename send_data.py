import psutil
import time
from influxdb import InfluxDBClient
import datetime
import socket
import subprocess

# InfluxDB-Verbindungsdetails
influxdb_host = "45.149.78.188"
influxdb_port = 8086
username = "myuser"
password = "mypassword"
database = "mydatabase"

client = InfluxDBClient(host=influxdb_host, port=influxdb_port, username=username, password=password, database=database)

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

# Funktion zur Abfrage des aktuellen Stromverbrauchs (Beispiel)
def get_power_consumption():
    try:
        with open('/sys/class/power_supply/energy_now', 'r') as f:
            power = f.readline()
        return float(power) / 1000000.0  # Umrechnung in Watt
    except FileNotFoundError:
        print("Power consumption file not found.")
        return None

# Initialwerte für die Netzwerkschnittstelle
net_io = psutil.net_io_counters()
prev_upload = net_io.bytes_sent
prev_download = net_io.bytes_recv

# Hostname des Systems
hostname = socket.gethostname()
print(f"Hostname: {hostname}")

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
    
    # Aktuelle Spannung in Volt
    voltage = get_voltage()

    json_body = [
        {
            "measurement": "system",
            "tags": {
                "host": hostname
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
                "power_consumption": power_consumption,  # Watt
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
