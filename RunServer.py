import subprocess

# Skripte ausführen
dashboard_server = subprocess.Popen(['python', 'dashboard_server.py'])
server = subprocess.Popen(['python', 'server.py'])
auth_server = subprocess.Popen(['python', 'auth_server.py'])
login_server = subprocess.Popen(['python', 'login_server.py'])
registration_server = subprocess.Popen(['python', 'registration_server.py'])

# Optional: auf Prozesse warten
#server_process.wait()
#login_process.wait()
