#!/bin/bash

# Navigate and extract public IP directly from the terraform output
EC2_IP=$(cd ../terraform && terraform output -raw public_ip)
echo $EC2_IP

# Check if a valid IP was extrated
if [ -z "$EC2_IP" ] || [[ "$EC2_IP" == *"No outputs"* ]]; then
  echo "Error: Could not extract the public IP from Terraform!"
  exit 1
fi

# Generate the inventory file
cat > inventory <<EOF
[agents]
agent-1 ansible_host=192.168.56.102 ansible_user=vm1
agent-2 ansible_host=192.168.56.103 ansible_user=vm2

[monitoring]
aws-monitor ansible_host=$EC2_IP ansible_user=ubuntu
EOF