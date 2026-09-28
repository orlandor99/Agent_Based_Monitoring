#!/bin/bash

# Read the EC2 public IP from Terraform state.
# Run this script from the bash/ directory.
EC2_IP=$(cd ../terraform && terraform output -raw public_ip)

# Use the configured URL when provided; otherwise, use the EC2 public IP.
SERVER_URL="${MONITORING_SERVER_URL:-http://$EC2_IP:5000}"

# Print the report header.
echo
echo "========================================"
echo "       MONITORING MACHINES SUMMARY"
echo "========================================"
echo

# Request the list of registered machines from the monitoring API.
machines=$(curl -s --fail "$SERVER_URL/machines")

# Stop if the monitoring server cannot be reached.
if [ $? -ne 0 ]; then
    echo "ERROR: Could not connect to monitoring server."
    exit 1
fi

# Count the machines returned by the API.
machine_count=$(echo "$machines" | jq '.machines | length')

# Exit normally when no machines have registered yet
if [ "$machine_count" -eq 0 ]; then
    echo "No monitored machines found."
    exit 0
fi

# Request and print the latest metrics for each registered machine.
echo "$machines" | jq -r '.machines[]' | while read -r hostname; do

    metrics=$(curl -s --fail "$SERVER_URL/machines/$hostname")

    # Report the error for this host and continue with the next one.
    if [ $? -ne 0 ]; then
        echo "Machine: $hostname"
        echo "ERROR: Could not retrieve metrics."
        echo
        continue
    fi

    # Extract the metric values from the JSON response.
    cpu=$(echo "$metrics" | jq -r '.metrics.cpu')
    memory=$(echo "$metrics" | jq -r '.metrics.memory.percent')
    disk=$(echo "$metrics" | jq -r '.metrics.disk.percent')
    processes=$(echo "$metrics" | jq -r '.metrics.processes')
    timestamp=$(echo "$metrics" | jq -r '.metrics.timestamp')

    # Display the latest metrics in a readable format.
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

# Print the total number of registered machines.
echo "Total machines: $machine_count"
echo "========================================"