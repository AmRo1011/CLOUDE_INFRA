variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "service_name" {
  description = "Service name for the bucket (e.g., user-management, document-service)"
  type        = string
}

variable "versioning_enabled" {
  description = "Enable versioning for the bucket"
  type        = bool
  default     = true
}

variable "lifecycle_rules_enabled" {
  description = "Enable lifecycle rules"
  type        = bool
  default     = true
}

variable "transition_to_ia_days" {
  description = "Days before transitioning to Infrequent Access"
  type        = number
  default     = 30
}

variable "transition_to_glacier_days" {
  description = "Days before transitioning to Glacier"
  type        = number
  default     = 90
}

variable "expiration_days" {
  description = "Days before object expiration (0 to disable)"
  type        = number
  default     = 0
}

variable "enable_encryption" {
  description = "Enable server-side encryption"
  type        = bool
  default     = true
}

variable "block_public_access" {
  description = "Block all public access"
  type        = bool
  default     = true
}

variable "enable_cors" {
  description = "Enable CORS configuration"
  type        = bool
  default     = false
}

variable "cors_allowed_origins" {
  description = "Allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allowed_methods" {
  description = "Allowed methods for CORS"
  type        = list(string)
  default     = ["GET", "POST", "PUT", "DELETE"]
}

variable "cors_allowed_headers" {
  description = "Allowed headers for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

