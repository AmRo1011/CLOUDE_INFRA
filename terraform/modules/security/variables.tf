variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block for internal rules"
  type        = string
}

variable "allowed_ssh_cidr_blocks" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Restrict this in production
}

variable "allowed_http_cidr_blocks" {
  description = "CIDR blocks allowed for HTTP/HTTPS access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

