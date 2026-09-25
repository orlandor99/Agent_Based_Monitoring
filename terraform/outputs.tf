output "instance_id" {
  value = aws_instance.monitor.id
}

output "public_ip" {
  value = aws_instance.monitor.public_ip
}

output "public_dns" {
  value = aws_instance.monitor.public_dns
}