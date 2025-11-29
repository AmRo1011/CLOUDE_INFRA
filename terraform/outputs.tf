# ============================================
# Network Outputs
# ============================================
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "Private app subnet IDs"
  value       = module.vpc.private_app_subnet_ids
}

# ============================================
# EC2 Outputs
# ============================================
output "nginx_public_ip" {
  description = "Nginx gateway public IP"
  value       = module.ec2_nginx.public_ip
}

output "nginx_instance_id" {
  description = "Nginx instance ID"
  value       = module.ec2_nginx.instance_id
}

output "app1_private_ip" {
  description = "App node 1 private IP"
  value       = module.ec2_app1.private_ip
}

output "app1_instance_id" {
  description = "App node 1 instance ID"
  value       = module.ec2_app1.instance_id
}

output "app2_private_ip" {
  description = "App node 2 private IP"
  value       = module.ec2_app2.private_ip
}

output "app2_instance_id" {
  description = "App node 2 instance ID"
  value       = module.ec2_app2.instance_id
}

output "kafka_private_ip" {
  description = "Kafka node private IP"
  value       = module.ec2_kafka.private_ip
}

output "kafka_instance_id" {
  description = "Kafka instance ID"
  value       = module.ec2_kafka.instance_id
}

# ============================================
# RDS Outputs
# ============================================
output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_endpoint
}

output "rds_address" {
  description = "RDS address"
  value       = module.rds.db_address
}

output "rds_port" {
  description = "RDS port"
  value       = module.rds.db_port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = module.rds.db_name
}

# ============================================
# S3 Outputs
# ============================================
output "s3_user_management_bucket" {
  description = "User management S3 bucket name"
  value       = module.s3_user_management.bucket_name
}

output "s3_document_bucket" {
  description = "Document service S3 bucket name"
  value       = module.s3_document.bucket_name
}

output "s3_quiz_bucket" {
  description = "Quiz service S3 bucket name"
  value       = module.s3_quiz.bucket_name
}

# ============================================
# Connection Information
# ============================================
output "connection_info" {
  description = "Connection information for services"
  value = {
    api_gateway_url = "http://${module.ec2_nginx.public_ip}"
    ssh_nginx       = "ssh -i <your-key>.pem ec2-user@${module.ec2_nginx.public_ip}"
    kafka_brokers   = "${module.ec2_kafka.private_ip}:9092"
    database_host   = module.rds.db_address
  }
}

# ============================================
# Service Configuration
# ============================================
output "service_urls" {
  description = "Service endpoints"
  value = {
    chat_service         = "http://${module.ec2_nginx.public_ip}/api/chat"
    user_management      = "http://${module.ec2_nginx.public_ip}/api/users"
    auth                 = "http://${module.ec2_nginx.public_ip}/api/auth"
    document_service     = "http://${module.ec2_nginx.public_ip}/api/documents"
    quiz_service         = "http://${module.ec2_nginx.public_ip}/api/quiz"
  }
}

