#!/bin/bash

SERVER_URL="http://192.168.56.101:5000"
HEADER="================================"
set -o pipefail

machines=$(curl -fs --connect-timeout 5 "$SERVER_URL/machines" | jq -r '.machines[]')

if [ $? -ne 0 ]; then
    echo "Error: Unable to fetch machines from server."
    exit 1
fi

for machine in $machines; do
    echo "$HEADER"
    echo "Monitoring machine: $machine"
    echo "$HEADER"
    curl -fs --connect-timeout 5 "$SERVER_URL/machines/$machine" | jq -r '
    .metrics |
    "cpu: \(.cpu)",
    "memory: \(.memory.percent)",
    "disk: \(.disk.percent)",
    "processes: \(.processes)"
'
done
