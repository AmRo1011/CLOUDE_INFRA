# ============================================
# VPC Module
# ============================================
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones

  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway

  tags = var.additional_tags
}

# ============================================
# Security Groups Module
# ============================================
module "security" {
  source = "./modules/security"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  vpc_cidr     = module.vpc.vpc_cidr

  allowed_ssh_cidr_blocks = var.allowed_ssh_cidr_blocks

  tags = var.additional_tags

  depends_on = [module.vpc]
}

# ============================================
# RDS PostgreSQL
# ============================================
module "rds" {
  source = "./modules/rds_postgres"

  project_name = var.project_name
  environment  = var.environment

  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password

  instance_class      = var.db_instance_class
  allocated_storage   = var.db_allocated_storage
  storage_type        = "gp3"
  multi_az            = false
  storage_encrypted   = true
  publicly_accessible = false

  db_subnet_group_name   = module.vpc.db_subnet_group_name
  vpc_security_group_ids = [module.security.db_sg_id]

  backup_retention_period = 7
  skip_final_snapshot     = var.environment == "dev" ? true : false
  deletion_protection     = var.environment == "prod" ? true : false

  tags = var.additional_tags

  depends_on = [module.vpc, module.security]
}

# ============================================
# S3 Buckets
# ============================================

# User Management Service Bucket
module "s3_user_management" {
  source = "./modules/s3_bucket"

  project_name = var.project_name
  environment  = var.environment
  service_name = "user-management"

  versioning_enabled      = true
  lifecycle_rules_enabled = var.enable_s3_lifecycle
  enable_encryption       = true
  block_public_access     = true

  tags = var.additional_tags
}

# Document Service Bucket
module "s3_document" {
  source = "./modules/s3_bucket"

  project_name = var.project_name
  environment  = var.environment
  service_name = "document-service"

  versioning_enabled      = true
  lifecycle_rules_enabled = var.enable_s3_lifecycle
  enable_encryption       = true
  block_public_access     = true
  enable_cors             = true

  tags = var.additional_tags
}

# Quiz Service Bucket
module "s3_quiz" {
  source = "./modules/s3_bucket"

  project_name = var.project_name
  environment  = var.environment
  service_name = "quiz-service"

  versioning_enabled      = true
  lifecycle_rules_enabled = var.enable_s3_lifecycle
  enable_encryption       = true
  block_public_access     = true

  tags = var.additional_tags
}

# ============================================
# EC2 Instances
# ============================================

# Nginx Gateway
module "ec2_nginx" {
  source = "./modules/ec2_instance"

  project_name  = var.project_name
  environment   = var.environment
  instance_name = "${var.project_name}-${var.environment}-nginx"

  instance_type          = var.nginx_instance_type
  subnet_id              = module.vpc.public_subnet_ids[0]
  vpc_security_group_ids = [module.security.nginx_sg_id]
  associate_public_ip    = true
  key_name               = var.ec2_key_name

  user_data = templatefile("${path.module}/templates/user_data_nginx.sh", {
    CHAT_SERVICE_HOST      = module.ec2_app1.private_ip
    USER_MGMT_SERVICE_HOST = module.ec2_app1.private_ip
    DOCUMENT_SERVICE_HOST  = module.ec2_app2.private_ip
    QUIZ_SERVICE_HOST      = module.ec2_app2.private_ip
  })

  root_volume_size = 20
  root_volume_type = "gp3"

  tags = merge(
    var.additional_tags,
    {
      Role = "nginx-gateway"
    }
  )

  depends_on = [module.vpc, module.security]
}

# Application Node 1 (Chat + User Management)
module "ec2_app1" {
  source = "./modules/ec2_instance"

  project_name  = var.project_name
  environment   = var.environment
  instance_name = "${var.project_name}-${var.environment}-app1"

  instance_type          = var.app_instance_type
  subnet_id              = module.vpc.private_app_subnet_ids[0]
  vpc_security_group_ids = [module.security.app_sg_id]
  associate_public_ip    = false
  key_name               = var.ec2_key_name

  user_data = templatefile("${path.module}/templates/user_data_app.sh", {
    DB_HOST               = module.rds.db_address
    DB_NAME               = var.db_name
    DB_USER               = var.db_username
    DB_PASSWORD           = var.db_password
    KAFKA_BROKERS         = "${module.ec2_kafka.private_ip}:9092"
    AWS_REGION            = var.aws_region
    S3_BUCKET_USER_MGMT   = module.s3_user_management.bucket_name
    S3_BUCKET_DOCUMENT    = module.s3_document.bucket_name
    S3_BUCKET_QUIZ        = module.s3_quiz.bucket_name
    ENVIRONMENT           = var.environment
    INSTANCE_NAME         = "${var.project_name}-${var.environment}-app1"
  })

  root_volume_size = 20
  root_volume_type = "gp3"

  tags = merge(
    var.additional_tags,
    {
      Role     = "app-node"
      Services = "chat,user-management"
    }
  )

  depends_on = [module.vpc, module.security, module.rds]
}

# Application Node 2 (Document + Quiz)
module "ec2_app2" {
  source = "./modules/ec2_instance"

  project_name  = var.project_name
  environment   = var.environment
  instance_name = "${var.project_name}-${var.environment}-app2"

  instance_type          = var.app_instance_type
  subnet_id              = module.vpc.private_app_subnet_ids[1]
  vpc_security_group_ids = [module.security.app_sg_id]
  associate_public_ip    = false
  key_name               = var.ec2_key_name

  user_data = templatefile("${path.module}/templates/user_data_app.sh", {
    DB_HOST               = module.rds.db_address
    DB_NAME               = var.db_name
    DB_USER               = var.db_username
    DB_PASSWORD           = var.db_password
    KAFKA_BROKERS         = "${module.ec2_kafka.private_ip}:9092"
    AWS_REGION            = var.aws_region
    S3_BUCKET_USER_MGMT   = module.s3_user_management.bucket_name
    S3_BUCKET_DOCUMENT    = module.s3_document.bucket_name
    S3_BUCKET_QUIZ        = module.s3_quiz.bucket_name
    ENVIRONMENT           = var.environment
    INSTANCE_NAME         = "${var.project_name}-${var.environment}-app2"
  })

  root_volume_size = 20
  root_volume_type = "gp3"

  tags = merge(
    var.additional_tags,
    {
      Role     = "app-node"
      Services = "document,quiz"
    }
  )

  depends_on = [module.vpc, module.security, module.rds]
}

# Kafka Node
module "ec2_kafka" {
  source = "./modules/ec2_instance"

  project_name  = var.project_name
  environment   = var.environment
  instance_name = "${var.project_name}-${var.environment}-kafka"

  instance_type          = var.kafka_instance_type
  subnet_id              = module.vpc.private_app_subnet_ids[0]
  vpc_security_group_ids = [module.security.kafka_sg_id]
  associate_public_ip    = false
  key_name               = var.ec2_key_name

  user_data = templatefile("${path.module}/templates/user_data_kafka.sh", {
    BROKER_ID  = "1"
    PRIVATE_IP = "" # Will be set automatically by instance
  })

  root_volume_size = 20
  root_volume_type = "gp3"

  additional_ebs_volumes = [
    {
      device_name = "/dev/xvdf"
      volume_size = var.kafka_ebs_volume_size
      volume_type = "gp3"
    }
  ]

  tags = merge(
    var.additional_tags,
    {
      Role = "kafka-broker"
    }
  )

  depends_on = [module.vpc, module.security]
}

