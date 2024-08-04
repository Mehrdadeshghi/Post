from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import time

def load_registered_controllers():
    try:
        with open('registered_controllers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Auth0-Domain und Client-ID
AUTH0_DOMAIN = 'your-tenant-name.auth0.com'  # Ersetze dies durch deine Auth0-Domain
AUTH0_CLIENT_ID = 'YOUR_CLIENT_ID'  # Ersetze dies durch deine Auth0-Client-ID

LOGOUT_URL = 'https://dev-yyhasue2lro86ieb.us.auth0.com/v2/logout?client_id=9HFGG9qfA31pOVYDfHZIB9ZTSD3jknx3&returnTo=http://45.149.78.188:8080/login'

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/dashboard'):
            registered_controllers = load_registered_controllers()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            response = """
            <!doctype html>
            <html>
            <head>
                <title>Raspberry Pi Dashboard</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                    .box {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 20px;
                    }
                    .box-item {
                        flex: 1;
                        background-color: #f9f9f9;
                        padding: 20px;
                        margin-right: 10px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    .box-item:last-child {
                        margin-right: 0;
                    }
                    .chart-container {
                        position: relative;
                        height: 400px;
                        width: 100%;
                    }
                    .logout-button {
                        background-color: #f44336;
                        color: white;
                        padding: 10px 20px;
                        text-align: center;
                        display: inline-block;
                        font-size: 16px;
                        margin: 10px 2px;
                        cursor: pointer;
                        text-decoration: none;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Raspberry Pi Dashboard</h1>
                    <a href="/logout" class="logout-button">Logout</a>
                    <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search for controllers..">
                    <table id="controllersTable">
                        <tr>
                            <th>Controller Name</th>
                            <th>Local IP Address</th>
                            <th>Public IP Address</th>
                            <th>Actions</th>
                        </tr>
            """
            for controller in registered_controllers:
                response += f"""
                        <tr>
                            <td>{controller['hostname']}</td>
                            <td>{controller['local_ip']}</td>
                            <td>{controller['public_ip']}</td>
                            <td>
                                <a href="/systeminfo?id={controller['hostname']}" class="system-info-button">System Info</a>
                                <a href="http://{controller['public_ip']}:5000" target="_blank" class="flask-link-button">Go to Flask</a>
                            </td>
                        </tr>
                """
            response += """
                    </table>
                </div>
                <script>
                    function filterTable() {
                        var input, filter, table, tr, td, i, txtValue;
                        input = document.getElementById("searchInput");
                        filter = input.value.toUpperCase();
                        table = document.getElementById("controllersTable");
                        tr = table.getElementsByTagName("tr");
                        for (i = 1; i < tr.length; i++) {
                            td = tr[i].getElementsByTagName("td")[0];
                            if (td) {
                                txtValue = td.textContent || td.innerText;
                                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                                    tr[i].style.display = "";
                                } else {
                                    tr[i].style.display = "none";
                                }
                            }
                        }
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(response.encode('utf-8'))
        elif self.path.startswith('/systeminfo'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            hostname = params['id'][0]
            registered_controllers = load_registered_controllers()
            controller = next((c for c in registered_controllers if c['hostname'] == hostname), None)

            if controller:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = f"""
                <!doctype html>
                <html>
                <head>
                    <title>System Info for {controller['hostname']}</title>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f0f0f0;
                        }}
                        .container {{
                            width: 80%;
                            margin: 20px auto;
                            background-color: #fff;
                            padding: 20px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        h1 {{
                            text-align: center;
                            color: #333;
                        }}
                        .box {{
                            display: flex;
                            justify-content: space-between;
                            margin-bottom: 20px;
                        }}
                        .box-item {{
                            flex: 1;
                            background-color: #f9f9f9;
                            padding: 20px;
                            margin-right: 10px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        .box-item:last-child {{
                            margin-right: 0;
                        }}
                        .chart-container {{
                            position: relative;
                            height: 400px;
                            width: 100%;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>System Info for {controller['hostname']}</h1>
                        <div class="box">
                            <div class="box-item">
                                <h2>Local IP Address</h2>
                                <p>{controller['local_ip']}</p>
                            </div>
                            <div class="box-item">
                                <h2>Public IP Address</h2>
                                <p>{controller['public_ip']}</p>
                            </div>
                            <div class="box-item">
                                <h2>Hostname</h2>
                                <p>{controller['hostname']}</p>
                            </div>
                        </div>
                        <div class="box">
                            <div class="box-item">
                                <h2>Uptime</h2>
                                <p>{controller['uptime']}</p>
                            </div>
                            <div class="box-item">
                                <h2>Load</h2>
                                <p>{controller['load']}</p>
                            </div>
                            <div class="box-item">
                                <h2>Memory</h2>
                                <p>{controller['memory'] / (1024 ** 3):.2f} GB</p>
                            </div>
                        </div>
                        <div class="box">
                            <div class="box-item">
                                <h2>Disk</h2>
                                <p>{controller['disk'] / (1024 ** 3):.2f} GB</p>
                            </div>
                            <div class="box-item">
                                <h2>RX Bytes</h2>
                                <p>{controller['rx_bytes']}</p>
                            </div>
                            <div class="box-item">
                                <h2>TX Bytes</h2>
                                <p>{controller['tx_bytes']}</p>
                            </div>
                        </div>
                        <div class="box">
                            <div class="box-item">
                                <h2>CPU Temp</h2>
                                <p>{controller['cpu_temp']}°C</p>
                            </div>
                        </div>
                        <h2>Connected Pins</h2>
                        <table>
                            <tr>
                                <th>Pin</th>
                                <th>Status</th>
                            </tr>
                            <!-- Hier sollten die verbundenen Pins aufgelistet werden -->
                        </table>
                        <h2>System Load</h2>
                        <div class="chart-container">
                            <canvas id="loadChart"></canvas>
                        </div>
                    </div>
                    <script>
                        var ctx = document.getElementById('loadChart').getContext('2d');
                        var loadChart = new Chart(ctx, {{
                            type: 'line',
                            data: {{
                                labels: ['1 min', '5 min', '15 min'],
                                datasets: [{{
                                    label: 'Load Average',
                                    data: {controller['load']},
                                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                    borderColor: 'rgba(75, 192, 192, 1)',
                                    borderWidth: 1
                                }}]
                            }},
                            options: {{
                                scales: {{
                                    yAxes: [{{
                                        ticks: {{
                                            beginAtZero: true
                                        }}
                                    }}]
                                }}
                            }}
                        }});
                    </script>
                </body>
                </html>
                """
                self.wfile.write(response.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Controller not found')
        elif self.path.startswith('/logout'):
            # Leitet den Benutzer zur Auth0-Logout-Seite weiter
            self.send_response(302)
            self.send_header('Location', LOGOUT_URL)
            self.endheaders()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run(server_class=HTTPServer, handler_class=DashboardHandler, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
