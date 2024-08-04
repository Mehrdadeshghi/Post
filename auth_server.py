from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import requests
import json

# Konfigurationsvariablen
AUTH0_CLIENT_ID = '6o3JOdcOVAGK5KS4fo1ZcT9JEPOG8t0u'
AUTH0_CLIENT_SECRET = 'E-4Xsdg1Y302ppXGAhsJ5MBM6ajRyh0HX4a1Dy-ymtHQSXqiN0v13MuEepljqxWE'
AUTH0_DOMAIN = 'dev-yyhasue2lro86ieb.us.auth0.com'  # Ersetze dies durch deine Auth0-Domain
REDIRECT_URI = 'http://45.149.78.188:8080/callback'  # Ersetze localhost durch deine Server-IP
DASHBOARD_URL = 'http://45.149.78.188:8000'

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/login'):
            # Leitet den Benutzer zur Auth0-Login-Seite weiter
            uri = f'https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20profile%20email'
            self.send_response(302)
            self.send_header('Location', uri)
            self.end_headers()
        elif self.path.startswith('/callback'):
            # Verarbeitet die Rückkehr von Auth0
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            code = params['code'][0]

            token_url = f'https://{AUTH0_DOMAIN}/oauth/token'
            token_payload = {
                'grant_type': 'authorization_code',
                'client_id': AUTH0_CLIENT_ID,
                'client_secret': AUTH0_CLIENT_SECRET,
                'code': code,
                'redirect_uri': REDIRECT_URI
            }

            token_info = requests.post(token_url, json=token_payload).json()
            access_token = token_info['access_token']

            userinfo_url = f'https://{AUTH0_DOMAIN}/userinfo'
            userinfo_headers = {
                'Authorization': f'Bearer {access_token}'
            }

            userinfo = requests.get(userinfo_url, headers=userinfo_headers).json()
            # Hier kannst du Benutzerinformationen verarbeiten
            print(json.dumps(userinfo, indent=4))

            # Überprüfe Benutzerrollen oder Berechtigungen
            if 'roles' in userinfo and 'Dashboard Access' in userinfo['roles']:
                self.send_response(302)
                self.send_header('Location', DASHBOARD_URL)
                self.end_headers()
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Forbidden')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run(server_class=HTTPServer, handler_class=AuthHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
