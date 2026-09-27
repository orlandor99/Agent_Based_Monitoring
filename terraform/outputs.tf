output "instance_id" {
  value       = aws_instance.monitor.id
  description = "EC2 instance ID"
}

output "public_ip" {
  value       = aws_instance.monitor.public_ip
  description = "EC2 public IP"
}

output "public_dns" {
  value = aws_instance.monitor.public_dns
}