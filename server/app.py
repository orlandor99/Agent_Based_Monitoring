
import os
import json
from flask import Flask, request, jsonify, render_template

DATA_FILE = '/server/data/metrics.json'

app = Flask(__name__)

@app.route('/metrics', methods=['POST'])
def metrics():
    # Read the new metric object from the request body.
    new_metric = request.get_json()
    
    # Load the existing metrics if the data file exists and is not empty.
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                saved_metrics = json.load(f)

                # Keep the stored data in a list for consistent handling.
                if not isinstance(saved_metrics, list):
                    saved_metrics = [saved_metrics]
            except json.JSONDecodeError:
                # Start with an empty list if the file contains invalid JSON.
                saved_metrics = []
    else:
        # Start with an empty list when the file does not exist or is empty.
        saved_metrics = []

    # Append the new sample to the stored metrics history.
    saved_metrics.append(new_metric)
    print("Saved metrics updated:", saved_metrics)

    # Save the complete metrics history back to the JSON file.
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(saved_metrics, f, indent=4)

    # Confirm that the metrics were received.
    return jsonify({"message": "Metrics received"}), 201

@app.route('/machines', methods=['GET'])
def machines():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                machines_data = json.load(f)
            except json.JSONDecodeError:
                machines_data = []
    else:
        machines_data = []

    # Build a unique list of hostnames found in the metrics history.
    machines = []
    for metric in machines_data:
        hostname = metric.get("hostname")
        if hostname and hostname not in machines:
            machines.append(hostname)

    # Return the registered hostnames.
    return jsonify({"machines": machines}), 200

@app.route('/machines/<hostname>', methods=['GET'])
def machine(hostname):
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                machines_data = json.load(f)
            except json.JSONDecodeError:
                machines_data = []
    else:
        machines_data = []

    # Select all saved samples for the requested hostname.
    machine_metrics = [
        metric for metric in machines_data
        if metric.get("hostname") == hostname
    ]

    if machine_metrics:
        # Return the most recently saved sample for this machine.
        latest_metrics = machine_metrics[-1]
        return jsonify({
            "hostname": hostname,
            "metrics": latest_metrics
        }), 200

    # Return 404 when no samples exist for the requested machine.
    return jsonify({
        "error": f"Machine '{hostname}' not found"
    }), 404

@app.route('/', methods=['GET'])
def dashboard():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                metrics_data = json.load(f)
            except json.JSONDecodeError:
                metrics_data = []
    else:
        metrics_data = []

    # Keep only the latest sample for each hostname.
    latest_metrics = {}

    for metric in metrics_data:
        hostname = metric.get("hostname")

        if hostname:
            latest_metrics[hostname] = metric

    machines = list(latest_metrics.values())

    # Calculate average memory and disk usage
    if machines:
        avg_memory = sum(
            machine["memory"]["percent"] for machine in machines
        ) / len(machines)

        avg_disk = sum(
            machine["disk"]["percent"] for machine in machines
        ) / len(machines)
    else:
        avg_memory = 0
        avg_disk = 0
        
    # Render the dashboard with the latest metrics and calculated averages.
    return render_template(
        'index.html',
        machines=machines,
        avg_memory=round(avg_memory, 1),
        avg_disk=round(avg_disk, 1)
    )
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

