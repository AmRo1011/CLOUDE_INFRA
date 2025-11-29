variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "cloud-learning-platform"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# EC2 Configuration
variable "ec2_key_name" {
  description = "SSH key pair name for EC2 instances"
  type        = string
  default     = ""
}

variable "nginx_instance_type" {
  description = "Instance type for Nginx gateway"
  type        = string
  default     = "t3.micro"
}

variable "app_instance_type" {
  description = "Instance type for application nodes"
  type        = string
  default     = "t3.small"
}

variable "kafka_instance_type" {
  description = "Instance type for Kafka node"
  type        = string
  default     = "t3.small"
}

variable "kafka_ebs_volume_size" {
  description = "EBS volume size for Kafka logs (GB)"
  type        = number
  default     = 50
}

# RDS Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "platform_main"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

# S3 Configuration
variable "enable_s3_lifecycle" {
  description = "Enable S3 lifecycle policies"
  type        = bool
  default     = true
}

# Security Configuration
variable "allowed_ssh_cidr_blocks" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Restrict this in production!
}

# Cost Optimization
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (disable to save costs)"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway instead of one per AZ"
  type        = bool
  default     = true
}

# Tags
variable "additional_tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}

