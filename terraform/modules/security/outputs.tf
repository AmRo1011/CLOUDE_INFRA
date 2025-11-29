output "nginx_sg_id" {
  description = "Security group ID for Nginx gateway"
  value       = aws_security_group.nginx.id
}

output "app_sg_id" {
  description = "Security group ID for application nodes"
  value       = aws_security_group.app.id
}

output "kafka_sg_id" {
  description = "Security group ID for Kafka cluster"
  value       = aws_security_group.kafka.id
}

output "db_sg_id" {
  description = "Security group ID for RDS database"
  value       = aws_security_group.db.id
}

output "bastion_sg_id" {
  description = "Security group ID for bastion host"
  value       = aws_security_group.bastion.id
}

