from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

registered_controllers = []

class RegisterHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            device_info = json.loads(post_data)
            required_fields = ['hostname', 'local_ip', 'public_ip', 'uptime', 'load', 'memory', 'disk', 'rx_bytes', 'tx_bytes', 'cpu_temp']
            if all(field in device_info for field in required_fields):
                # Aktualisiere oder füge den Controller hinzu
                for controller in registered_controllers:
                    if controller['hostname'] == device_info['hostname']:
                        controller.update(device_info)
                        controller['last_seen'] = time.time()
                        break
                else:
                    device_info['last_seen'] = time.time()
                    registered_controllers.append(device_info)
                self.save_registered_controllers()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Device registered successfully'}).encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Invalid data'}).encode())

    def save_registered_controllers(self):
        with open('registered_controllers.json', 'w') as f:
            json.dump(registered_controllers, f)

def run(server_class=HTTPServer, handler_class=RegisterHandler, port=8082):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting registration server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
