output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.main.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_eip.main.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.main.public_dns
}

output "ssh_connection_command" {
  description = "SSH connection command"
  value       = "ssh -i ~/.ssh/your-key.pem ubuntu@${aws_eip.main.public_ip}"
}

output "application_url" {
  description = "Application URL on port 8080"
  value       = "http://${aws_eip.main.public_ip}:8080"
}
