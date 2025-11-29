variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "db_name" {
  description = "Name of the default database to create"
  type        = string
  default     = "platform_main"
}

variable "db_username" {
  description = "Master username for database"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Master password for database"
  type        = string
  sensitive   = true
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage for autoscaling (0 to disable)"
  type        = number
  default     = 100
}

variable "storage_type" {
  description = "Storage type (gp2, gp3, io1)"
  type        = string
  default     = "gp3"
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.15"
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "publicly_accessible" {
  description = "Allow public access to database"
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "db_subnet_group_name" {
  description = "DB subnet group name"
  type        = string
}

variable "vpc_security_group_ids" {
  description = "List of VPC security group IDs"
  type        = list(string)
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when destroying"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = false
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch"
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

variable "performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = false
}

variable "storage_encrypted" {
  description = "Enable storage encryption"
  type        = bool
  default     = true
}

variable "parameter_family" {
  description = "DB parameter group family"
  type        = string
  default     = "postgres15"
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

