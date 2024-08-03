import requests
import socket
import time
import psutil

SERVER_URL = 'http://45.149.78.188:8082/register'  # URL des Servers zum Registrieren

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Verbinde zu einem externen Server, um die lokale IP-Adresse zu ermitteln
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def get_device_info():
    hostname = socket.gethostname()
    local_ip_address = get_local_ip()
    public_ip_address = requests.get('https://api.ipify.org').text

    # Systeminformationen erfassen
    uptime = time.time() - psutil.boot_time()
    load = psutil.getloadavg()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    cpu_temp = psutil.sensors_temperatures().get('cpu-thermal', [{}])[0].get('current', 'N/A')

    return {
        'hostname': hostname,
        'local_ip': local_ip_address,
        'public_ip': public_ip_address,
        'uptime': uptime,
        'load': load,
        'memory': memory.total,
        'disk': disk.total,
        'rx_bytes': net_io.bytes_recv,
        'tx_bytes': net_io.bytes_sent,
        'cpu_temp': cpu_temp
    }

def register_with_server():
    while True:
        try:
            device_info = get_device_info()
            response = requests.post(SERVER_URL, json=device_info)
            if response.status_code == 200:
                print('Successfully registered with the server')
            else:
                print(f'Failed to register: {response.status_code}')
        except Exception as e:
            print(f'Error: {e}')
        time.sleep(60)  # Melde jede Minute

if __name__ == '__main__':
    register_with_server()
