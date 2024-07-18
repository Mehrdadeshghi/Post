import psutil
from flask import Blueprint, render_template, jsonify

management_bp = Blueprint('management', __name__)

@management_bp.route('/')
def management_dashboard():
    return render_template('management.html')

@management_bp.route('/system_info')
def system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    return jsonify({
        "cpu_usage": cpu_usage,
        "memory_usage": memory,
        "disk_usage": disk_usage
    })
