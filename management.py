import os
import psutil
from flask import Flask, jsonify, render_template, send_file, Blueprint
import pandas as pd
import io
from datetime import datetime

# Initialize the Flask Blueprint for management
management_bp = Blueprint('management', __name__)

def get_system_info():
    """Retrieve system information including CPU usage, memory, and network activity."""
    cpu_temperature = float(os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", ""))
    uptime = os.popen("uptime -p").readline().strip()
    net_stats = os.popen("ifstat -i eth0 1 1").readlines()[-1].strip().split()
    upload = float(net_stats[0])
    download = float(net_stats[1])
    active_processes = len(psutil.pids())
    return cpu_temperature, uptime, upload, download, active_processes

@management_bp.route('/system_info')
def system_info():
    """Endpoint for retrieving and sending system information as JSON."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    disk_usage = psutil.disk_usage('/').percent
    cpu_temperature, uptime, upload, download, active_processes = get_system_info()
    return jsonify({
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "cpu_temperature": cpu_temperature,
        "system_uptime": uptime,
        "network_activity": {"upload": upload, "download": download},
        "active_processes": active_processes
    })

if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(management_bp, url_prefix='/management')
    app.run(host='0.0.0.0', port=5000)
