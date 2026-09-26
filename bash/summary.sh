#!/bin/bash

SERVER_URL="${MONITORING_SERVER_URL:-http://localhost:5000}"

echo
echo "========================================"
echo "       MONITORING MACHINES SUMMARY"
echo "========================================"
echo

machines=$(curl -s --fail "$SERVER_URL/machines")

if [ $? -ne 0 ]; then
    echo "ERROR: Could not connect to monitoring server."
    exit 1
fi

machine_count=$(echo "$machines" | jq '.machines | length')

if [ "$machine_count" -eq 0 ]; then
    echo "No monitored machines found."
    exit 0
fi

echo "$machines" | jq -r '.machines[]' | while read -r hostname; do

    metrics=$(curl -s --fail "$SERVER_URL/machines/$hostname")

    if [ $? -ne 0 ]; then
        echo "Machine: $hostname"
        echo "ERROR: Could not retrieve metrics."
        echo
        continue
    fi

    cpu=$(echo "$metrics" | jq -r '.metrics.cpu')
    memory=$(echo "$metrics" | jq -r '.metrics.memory.percent')
    disk=$(echo "$metrics" | jq -r '.metrics.disk.percent')
    processes=$(echo "$metrics" | jq -r '.metrics.processes')
    timestamp=$(echo "$metrics" | jq -r '.metrics.timestamp')

    echo "Machine:    $hostname"
    echo "CPU:        ${cpu}%"
    echo "Memory:     ${memory}%"
    echo "Disk:       ${disk}%"
    echo "Processes:  $processes"
    echo "Timestamp:  $timestamp"

    echo
    echo "----------------------------------------"
    echo

done

echo "Total machines: $machine_count"
echo "========================================"