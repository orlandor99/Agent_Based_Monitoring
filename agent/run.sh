#!/bin/bash
echo "Installing dependencies..."
python -m pip install -r requirements.txt
echo "Running agent.py..."
AGENT_INTERVAL=10 python agent.py

