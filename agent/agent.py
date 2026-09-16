import psutil
import socket
import time
import json
import os
import requests

def get_system_info():
    hostname = socket.gethostname()
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    processes = len(psutil.pids())
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    return {
        "hostname": hostname, 
        "cpu": cpu, 
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        },
        "disk": {
            "total": disk.total,
            "free": disk.free,
            "used": disk.used,
            "percent": disk.percent
        },
        "processes": processes,
        "timestamp": timestamp        
    }

interval = int(os.getenv("AGENT_INTERVAL", 5))  # Default interval is 5 seconds
server_url = os.getenv("MONITORING_SERVER_URL", "http://192.168.56.101:5000/metrics")  # Default server URL
##server_url = os.getenv("MONITORING_SERVER_URL", "http://localhost:5000/metrics")  # Default server URL

try:
    while True:
        data = get_system_info()
        try:
            response = requests.post(server_url, json=data)
            if response.status_code == 201:
                print(f"[{data['timestamp']}] Metrics sent successfully! Server response: {response.status_code}")
            else:
                print(f"[{data['timestamp']}] Failed to send metrics: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"[{data['timestamp']}] Error sending metrics: {e}" )

        time.sleep(interval)
except KeyboardInterrupt:
    print("Monitoring stopped.")


