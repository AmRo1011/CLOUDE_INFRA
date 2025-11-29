output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.main.id
}

output "instance_arn" {
  description = "EC2 instance ARN"
  value       = aws_instance.main.arn
}

output "private_ip" {
  description = "Private IP address"
  value       = aws_instance.main.private_ip
}

output "public_ip" {
  description = "Public IP address (if assigned)"
  value       = aws_instance.main.public_ip
}

output "availability_zone" {
  description = "Availability zone"
  value       = aws_instance.main.availability_zone
}

output "ebs_volume_ids" {
  description = "Additional EBS volume IDs"
  value       = aws_ebs_volume.additional[*].id
}

