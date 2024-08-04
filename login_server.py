from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import requests

# Konfigurationsvariablen
AUTH0_CLIENT_ID = '9HFGG9qfA31pOVYDfHZIB9ZTSD3jknx3'
AUTH0_CLIENT_SECRET = 'lNIlAKj8Mcwq-IxN5TfWvhWiRQoRszt0DdRgo7lqK8IzWXbhTtz38sBVR4pIkNDS'
AUTH0_DOMAIN = 'dev-yyhasue2lro86ieb.us.auth0.com'  # Ersetze dies durch deine Auth0-Domain
API_IDENTIFIER = 'https://raspberrypi.dashboard/api'
REDIRECT_URI = 'http://45.149.78.188:8080/callback'
DASHBOARD_URL = 'http://45.149.78.188:8081/dashboard'  # Beachte den Port für das Dashboard

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/login'):
            # Leitet den Benutzer zur Auth0-Login-Seite weiter
            uri = f'https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={REDIRECT_URI}&audience={API_IDENTIFIER}&scope=openid%20profile%20email'
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
            print(userinfo)

            self.send_response(302)
            self.send_header('Location', DASHBOARD_URL)
            self.end_headers()
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
