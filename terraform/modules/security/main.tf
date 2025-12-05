# Security Group for Nginx Gateway (Public-facing)
resource "aws_security_group" "nginx" {
  name        = "${var.project_name}-${var.environment}-nginx-sg"
  description = "Security group for Nginx gateway/load balancer"
  vpc_id      = var.vpc_id

  # HTTP
  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_http_cidr_blocks
  }

  # HTTPS
  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_http_cidr_blocks
  }

  # SSH (for management)
  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  # Outbound - allow all
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-nginx-sg"
      Environment = var.environment
      Tier        = "Public"
    },
    var.tags
  )
}

# Security Group for Application Nodes
resource "aws_security_group" "app" {
  name        = "${var.project_name}-${var.environment}-app-sg"
  description = "Security group for application microservices"
  vpc_id      = var.vpc_id

  # HTTP from Nginx
  ingress {
    description     = "HTTP from Nginx"
    from_port       = 8000
    to_port         = 8100
    protocol        = "tcp"
    security_groups = [aws_security_group.nginx.id]
  }

  # SSH (for management)
  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  # Allow inter-app communication (for service discovery)
  ingress {
    description = "Inter-app communication"
    from_port   = 8000
    to_port     = 8100
    protocol    = "tcp"
    self        = true
  }

  # Outbound - allow all
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-app-sg"
      Environment = var.environment
      Tier        = "PrivateApp"
    },
    var.tags
  )
}

# Security Group for Kafka Cluster
resource "aws_security_group" "kafka" {
  name        = "${var.project_name}-${var.environment}-kafka-sg"
  description = "Security group for Kafka brokers and Zookeeper"
  vpc_id      = var.vpc_id

  # Kafka broker port from app nodes
  ingress {
    description     = "Kafka broker from apps"
    from_port       = 9092
    to_port         = 9092
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # Zookeeper client port from app nodes
  ingress {
    description     = "Zookeeper client from apps"
    from_port       = 2181
    to_port         = 2181
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # Zookeeper peer communication (for multi-node setup)
  ingress {
    description = "Zookeeper peer communication"
    from_port   = 2888
    to_port     = 2888
    protocol    = "tcp"
    self        = true
  }

  # Zookeeper leader election
  ingress {
    description = "Zookeeper leader election"
    from_port   = 3888
    to_port     = 3888
    protocol    = "tcp"
    self        = true
  }

  # Inter-broker communication (for multi-broker setup)
  ingress {
    description = "Kafka inter-broker"
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    self        = true
  }

  # SSH from Nginx (bastion/jump host)
  ingress {
    description     = "SSH from Nginx bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.nginx.id]
  }

  # SSH (for management from internet - optional)
  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  # Outbound - allow all
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-kafka-sg"
      Environment = var.environment
      Tier        = "PrivateApp"
    },
    var.tags
  )
}

# Security Group for RDS Database
resource "aws_security_group" "db" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "Security group for RDS PostgreSQL database"
  vpc_id      = var.vpc_id

  # PostgreSQL from app nodes
  ingress {
    description     = "PostgreSQL from apps"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  # Outbound - allow all (for RDS managed operations)
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-db-sg"
      Environment = var.environment
      Tier        = "Database"
    },
    var.tags
  )
}

# Optional: Bastion Host Security Group (for troubleshooting)
resource "aws_security_group" "bastion" {
  name        = "${var.project_name}-${var.environment}-bastion-sg"
  description = "Security group for bastion host (optional)"
  vpc_id      = var.vpc_id

  # SSH from specific IPs
  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  # Outbound - allow all
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.environment}-bastion-sg"
      Environment = var.environment
      Tier        = "Public"
    },
    var.tags
  )
}

