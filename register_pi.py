import requests
import json
import subprocess

# Funktion zum Abrufen der Serialnummer
def get_serial():
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

# Systeminformationen sammeln
serial_number = get_serial()
model = "Raspberry Pi 4 Model B"  # Beispielmodell
os_version = subprocess.check_output(['uname', '-a']).decode().strip()
firmware_version = subprocess.check_output(['vcgencmd', 'version']).decode().strip()
ip_address = subprocess.check_output(['hostname', '-I']).decode().strip().split()[0]

# Daten vorbereiten
data = {
    "serial_number": serial_number,
    "model": model,
    "os_version": os_version,
    "firmware_version": firmware_version,
    "ip_address": ip_address
}

# HTTP-POST-Anfrage senden
url = "http://45.149.78.188:5000/register"
headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())
