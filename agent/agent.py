import os
import socket
import time

import psutil
import requests


def get_system_info():
    # Identify the current host and collect its system metrics.
    hostname = socket.gethostname()

    # Measure CPU usage over a one-second sampling interval.
    cpu = psutil.cpu_percent(interval=1)

    # Collect memory and root filesystem usage.
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Count running processes and create a local-time timestamp.
    processes = len(psutil.pids())
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Return the metrics in the JSON structure expected by the server.
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


# Read the polling interval from the environment; use 5 seconds by default.
interval = int(os.getenv("AGENT_INTERVAL", 5))

# Read the server endpoint from the environment.
server_url = os.getenv(
    "MONITORING_SERVER_URL",
    "http://localhost:5000/metrics"
)

try:
    while True:
        data = get_system_info()

        try:
            # Send the latest metrics to the central monitoring server.
            response = requests.post(server_url, json=data, timeout=5)

            if response.status_code == 201:
                print(
                    f"[{data['timestamp']}] Metrics sent successfully! "
                    f"Server response: {response.status_code}"
                )
            else:
                # Log unexpected responses and continue with the next cycle.
                print(
                    f"[{data['timestamp']}] Failed to send metrics: "
                    f"{response.status_code} - {response.text}"
                )

        except requests.RequestException as e:
            # Log connection errors without stopping the monitoring loop.
            print(f"[{data['timestamp']}] Error sending metrics: {e}")

        # Wait before collecting the next sample.
        time.sleep(interval)

except KeyboardInterrupt:
    # Exit cleanly when the user stops the agent with Ctrl+C.
    print("Monitoring stopped.")