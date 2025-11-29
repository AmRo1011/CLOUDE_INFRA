# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-postgres-params"
  family = var.parameter_family

  # Optimize for small instances - only dynamic parameters
  parameter {
    name  = "work_mem"
    value = "4096" # 4MB
    apply_method = "immediate"
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "65536" # 64MB
    apply_method = "immediate"
  }

  parameter {
    name  = "random_page_cost"
    value = "1.1" # For SSD storage
    apply_method = "immediate"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000" # Log slow queries (>1s)
    apply_method = "immediate"
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-postgres-params"
      Environment = var.environment
    },
    var.tags
  )
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-postgres"

  # Engine
  engine         = "postgres"
  engine_version = var.engine_version

  # Instance
  instance_class = var.instance_class

  # Storage
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = var.storage_encrypted

  # Database
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  # Network
  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = var.vpc_security_group_ids
  publicly_accessible    = var.publicly_accessible
  multi_az               = var.multi_az

  # Backup
  backup_retention_period = var.backup_retention_period
  backup_window           = var.backup_window
  maintenance_window      = var.maintenance_window
  skip_final_snapshot     = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Monitoring
  enabled_cloudwatch_logs_exports = var.enabled_cloudwatch_logs_exports
  performance_insights_enabled    = var.performance_insights_enabled
  monitoring_interval             = var.performance_insights_enabled ? 60 : 0

  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.main.name

  # Protection
  deletion_protection = var.deletion_protection

  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  # Apply changes immediately (for dev)
  apply_immediately = var.environment == "dev" ? true : false

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-postgres"
      Environment = var.environment
      Database    = var.db_name
    },
    var.tags
  )

  lifecycle {
    ignore_changes = [
      password,
      final_snapshot_identifier,
    ]
  }
}

