# S3 Bucket
resource "aws_s3_bucket" "main" {
  bucket = "${var.service_name}-storage-${var.environment}-${var.project_name}"

  tags = merge(
    {
      Name        = "${var.service_name}-storage-${var.environment}"
      Environment = var.environment
      Service     = var.service_name
      Project     = var.project_name
    },
    var.tags
  )

  lifecycle {
    prevent_destroy = false
  }
}

# Versioning
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = var.block_public_access
  block_public_policy     = var.block_public_access
  ignore_public_acls      = var.block_public_access
  restrict_public_buckets = var.block_public_access
}

# Lifecycle rules
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  count  = var.lifecycle_rules_enabled ? 1 : 0
  bucket = aws_s3_bucket.main.id

  # Transition to IA
  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = var.transition_to_ia_days
      storage_class = "STANDARD_IA"
    }

    filter {
      prefix = ""
    }
  }

  # Transition to Glacier
  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    transition {
      days          = var.transition_to_glacier_days
      storage_class = "GLACIER"
    }

    filter {
      prefix = ""
    }
  }

  # Expiration (if enabled)
  dynamic "rule" {
    for_each = var.expiration_days > 0 ? [1] : []
    content {
      id     = "expiration"
      status = "Enabled"

      expiration {
        days = var.expiration_days
      }

      filter {
        prefix = ""
      }
    }
  }

  # Clean up old versions
  rule {
    id     = "cleanup-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    filter {
      prefix = ""
    }
  }

  # Clean up incomplete multipart uploads
  rule {
    id     = "cleanup-multipart"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }

    filter {
      prefix = ""
    }
  }
}

# CORS configuration (optional)
resource "aws_s3_bucket_cors_configuration" "main" {
  count  = var.enable_cors ? 1 : 0
  bucket = aws_s3_bucket.main.id

  cors_rule {
    allowed_headers = var.cors_allowed_headers
    allowed_methods = var.cors_allowed_methods
    allowed_origins = var.cors_allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

