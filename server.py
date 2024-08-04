import http.server
import socketserver
import urllib.parse

clients = {}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))

        ip = self.client_address[0]
        clients[ip] = {
            'hostname': data.get('hostname', [''])[0],
            'ip': data.get('ip', [''])[0],
            'public_ip': data.get('public_ip', [''])[0],
            'status': data.get('status', [''])[0],
            'uptime': data.get('uptime', [''])[0],
            'load': data.get('load', [''])[0],
            'memory': data.get('memory', [''])[0],
            'disk': data.get('disk', [''])[0],
            'rx_bytes': data.get('rx_bytes', [''])[0],
            'tx_bytes': data.get('tx_bytes', [''])[0],
            'cpu_temp': data.get('cpu_temp', [''])[0]
        }

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Status updated")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        response = """
        <!doctype html>
        <html>
        <head>
            <title>Raspberry Pi Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f0;
                }
                .container {
                    width: 80%;
                    margin: 20px auto;
                    background-color: #fff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    text-align: center;
                    color: #333;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                th, td {
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f8f8f8;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .flask-link {
                    color: blue;
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Raspberry Pi Dashboard</h1>
                <table>
                    <tr>
                        <th>IP Address</th>
                        <th>Hostname</th>
                        <th>Status</th>
                        <th>Uptime</th>
                        <th>Load</th>
                        <th>Memory</th>
                        <th>Disk</th>
                        <th>RX Bytes (MB)</th>
                        <th>TX Bytes (MB)</th>
                        <th>CPU Temp (°C)</th>
                        <th>Flask Link</th>
                    </tr>
        """
        for ip, info in clients.items():
            response += f"""
                    <tr>
                        <td>{info['ip']}</td>
                        <td>{info['hostname']}</td>
                        <td>{info['status']}</td>
                        <td>{info['uptime']}</td>
                        <td>{info['load']}</td>
                        <td>{info['memory']}</td>
                        <td>{info['disk']}</td>
                        <td>{int(info['rx_bytes']) / (1024 * 1024):.2f} MB</td>
                        <td>{int(info['tx_bytes']) / (1024 * 1024):.2f} MB</td>
                        <td>{info['cpu_temp']} °C</td>
                        <td><a class="flask-link" href="http://{info['public_ip']}:5000" target="_blank">Go to Flask</a></td>
                    </tr>
            """
        response += """
                </table>
            </div>
        </body>
        </html>
        """

        self.wfile.write(response.encode('utf-8'))

PORT = 8000
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
