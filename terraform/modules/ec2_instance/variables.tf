variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "instance_name" {
  description = "Name for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID (leave empty for latest Amazon Linux 2)"
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "Subnet ID where instance will be launched"
  type        = string
}

variable "vpc_security_group_ids" {
  description = "List of security group IDs"
  type        = list(string)
}

variable "associate_public_ip" {
  description = "Associate public IP address"
  type        = bool
  default     = false
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = ""
}

variable "user_data" {
  description = "User data script"
  type        = string
  default     = ""
}

variable "root_volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 20
}

variable "root_volume_type" {
  description = "Root volume type"
  type        = string
  default     = "gp3"
}

variable "additional_ebs_volumes" {
  description = "List of additional EBS volumes to attach"
  type = list(object({
    device_name = string
    volume_size = number
    volume_type = string
  }))
  default = []
}

variable "enable_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = false
}

variable "iam_instance_profile" {
  description = "IAM instance profile name"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

