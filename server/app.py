
import os
import json
from flask import Flask, request, jsonify

DATA_FILE = '/server/data/metrics.json'

app = Flask(__name__)

@app.route('/metrics', methods=['POST'])
def metrics():
    # 1. Primește JSON-ul nou
    new_metric = request.get_json()
    
    # 2. Deschide și citește datele VECHI (dacă fișierul există și nu e gol)
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                saved_metrics = json.load(f)
                # Ne asigurăm că datele citite sunt o listă, nu un singur obiect
                if not isinstance(saved_metrics, list):
                    saved_metrics = [saved_metrics]
            except json.JSONDecodeError:
                saved_metrics = []
    else:
        saved_metrics = []

    # 3. Adaugă noua măsurătoare la cele vechi
    saved_metrics.append(new_metric)
    print("Saved metrics updated:", saved_metrics)

    # 4. Salvează TOATE datele (istoricul complet + noua măsurătoare)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(saved_metrics, f, indent=4)

    # 5. Returnează răspunsul
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
    machines = []
    for metric in machines_data:
        hostname = metric.get("hostname")
        if hostname and hostname not in machines:
            machines.append(hostname)
    # Implement logic to retrieve machine information
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

    machine_metrics = [
        metric for metric in machines_data
        if metric.get("hostname") == hostname
    ]

    if machine_metrics:
        latest_metrics = machine_metrics[-1]
        return jsonify({
            "hostname": hostname,
            "metrics": latest_metrics
        }), 200

    return jsonify({
        "error": f"Machine '{hostname}' not found"
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

