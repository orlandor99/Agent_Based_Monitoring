
import os
import json
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta, timezone

DATA_FILE = '/server/data/metrics.json'

app = Flask(__name__)

@app.route('/metrics', methods=['POST'])
def metrics():
    # Read the new metric object from the request body.
    new_metric = request.get_json()

    if not isinstance(new_metric, dict):
        return jsonify({"error": "Metric must be a JSON object"}), 400

    # Load the existing metrics if the data file exists and is not empty.
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                saved_metrics = json.load(f)

                # Keep the stored data in a list for consistent handling.
                if not isinstance(saved_metrics, list):
                    saved_metrics = [saved_metrics]
            except json.JSONDecodeError:
                saved_metrics = []
    else:
        saved_metrics = []

    # Use the server's receive time for retention, so agent clock differences
    # do not affect which metrics expire.
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)
    new_metric["received_at"] = now.isoformat()
    saved_metrics.append(new_metric)

    # Retain only metrics received within the last seven days.
    retained_metrics = []
    for metric in saved_metrics:
        if not isinstance(metric, dict):
            continue

        received_at = metric.get("received_at")

        # Give existing records without a receive time seven days from this update.
        if not received_at:
            received_at = now.isoformat()
            metric["received_at"] = received_at

        try:
            received_at = datetime.fromisoformat(received_at)
            if received_at.tzinfo is None:
                received_at = received_at.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue

        if received_at >= cutoff:
            retained_metrics.append(metric)

    # Save the retained metrics back to the JSON file.
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(retained_metrics, f, indent=4)

    app.logger.info(
        "Metrics received from %s",
        new_metric.get("hostname", "unknown")
    )

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
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

