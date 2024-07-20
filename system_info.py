import os
import psutil

def get_system_info():
    try:
        cpu_temperature = float(os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", ""))
    except Exception as e:
        print(f"Error fetching CPU temperature: {e}")
        cpu_temperature = 0  # Default value if the command fails

    try:
        uptime = os.popen("uptime -p").readline().strip()
    except Exception as e:
        print(f"Error fetching uptime: {e}")
        uptime = "N/A"

    try:
        net_stats = os.popen("ifstat -i eth0 1 1").readlines()[-1].strip().split()
        upload = float(net_stats[0])
        download = float(net_stats[1])
    except Exception as e:
        print(f"Error fetching network stats: {e}")
        upload = 0
        download = 0

    active_processes = len(psutil.pids())
    
    return cpu_temperature, uptime, upload, download, active_processes
