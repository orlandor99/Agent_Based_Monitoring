#!/bin/bash

EC2_IP=$(cd ../terraform && terraform output -raw public_ip)

cat <<EOF
[agents]
agent-1 ansible_host=192.168.56.102 ansible_user=vm1
agent-2 ansible_host=192.168.56.103 ansible_user=vm2

[monitoring]
aws-monitor ansible_host=$EC2_IP ansible_user=ubuntu
EOF