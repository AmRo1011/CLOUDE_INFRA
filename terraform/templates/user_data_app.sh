#!/bin/bash
set -e

# Update system
yum update -y

# Install Docker
amazon-linux-extras install docker -y
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
yum install git -y

# Install Python 3.9 (for future deployment scripts)
amazon-linux-extras install python3.8 -y

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Create application directory
mkdir -p /opt/app
chown ec2-user:ec2-user /opt/app

# Create docker network for services
docker network create app-network 2>/dev/null || true

# Create environment file placeholder
cat > /opt/app/.env << 'EOF'
# Environment variables for services
# These will be populated during deployment

# Database configuration
DB_HOST=${DB_HOST}
DB_PORT=5432
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# Kafka configuration
KAFKA_BROKERS=${KAFKA_BROKERS}

# S3 configuration
AWS_REGION=${AWS_REGION}
S3_BUCKET_USER_MGMT=${S3_BUCKET_USER_MGMT}
S3_BUCKET_DOCUMENT=${S3_BUCKET_DOCUMENT}
S3_BUCKET_QUIZ=${S3_BUCKET_QUIZ}

# Service configuration
ENVIRONMENT=${ENVIRONMENT}
LOG_LEVEL=INFO
EOF

chown ec2-user:ec2-user /opt/app/.env

# Install CloudWatch agent
yum install amazon-cloudwatch-agent -y

# Configure CloudWatch logs
cat > /opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-config.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/aws/ec2/${INSTANCE_NAME}",
            "log_stream_name": "{instance_id}/messages"
          },
          {
            "file_path": "/var/log/docker",
            "log_group_name": "/aws/ec2/${INSTANCE_NAME}",
            "log_stream_name": "{instance_id}/docker"
          }
        ]
      }
    }
  }
}
EOF

# Create systemd service for container management
cat > /etc/systemd/system/app-containers.service << 'EOF'
[Unit]
Description=Application Containers
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/app
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ec2-user

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

# Log completion
echo "App node setup completed at $(date)" > /var/log/user-data-complete.log

