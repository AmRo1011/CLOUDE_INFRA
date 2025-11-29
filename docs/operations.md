# Operations Guide - Cloud Learning Platform

## Daily Operations

### Starting Your Work Session

```bash
# 1. Navigate to terraform directory
cd terraform

# 2. Check current state
terraform show

# 3. Apply infrastructure (if destroyed)
terraform apply -auto-approve

# 4. Get connection info
terraform output
```

### Ending Your Work Session

#### Option 1: Stop Instances (Saves ~50% cost)

```bash
# Stop all EC2 instances
aws ec2 stop-instances --instance-ids \
  $(terraform output -raw nginx_instance_id) \
  $(terraform output -raw app1_instance_id) \
  $(terraform output -raw app2_instance_id) \
  $(terraform output -raw kafka_instance_id)

# RDS will continue running (or stop manually)
aws rds stop-db-instance --db-instance-identifier <rds-id>
```

#### Option 2: Destroy Everything (Maximum savings)

```bash
# WARNING: All data will be lost!
terraform destroy -auto-approve

# Commit your code changes first!
git add .
git commit -m "Save progress before destroy"
git push
```

---

## Common Tasks

### Accessing Instances

#### SSH to Nginx Gateway (Public)

```bash
ssh -i your-key.pem ec2-user@$(terraform output -raw nginx_public_ip)
```

#### SSH to App Nodes (Through Bastion)

```bash
# Method 1: Two-step
ssh -i your-key.pem ec2-user@<nginx-public-ip>
# Then from nginx:
ssh ec2-user@<app-private-ip>

# Method 2: One command with ProxyJump
ssh -i your-key.pem -J ec2-user@<nginx-public-ip> ec2-user@<app-private-ip>
```

#### SSH Config for Easier Access

Add to `~/.ssh/config`:

```
Host cloud-nginx
  HostName <nginx-public-ip>
  User ec2-user
  IdentityFile ~/.ssh/your-key.pem

Host cloud-app1
  HostName <app1-private-ip>
  User ec2-user
  IdentityFile ~/.ssh/your-key.pem
  ProxyJump cloud-nginx

Host cloud-app2
  HostName <app2-private-ip>
  User ec2-user
  IdentityFile ~/.ssh/your-key.pem
  ProxyJump cloud-nginx

Host cloud-kafka
  HostName <kafka-private-ip>
  User ec2-user
  IdentityFile ~/.ssh/your-key.pem
  ProxyJump cloud-nginx
```

Then simply:
```bash
ssh cloud-nginx
ssh cloud-app1
```

---

## Database Operations

### Connecting to RDS

#### From App Node

```bash
# SSH to app node first
ssh cloud-app1

# Install psql client (if not present)
sudo yum install postgresql -y

# Connect
psql -h $(terraform output -raw rds_address) \
     -U postgres \
     -d platform_main
```

#### Create Service Schemas

```sql
-- User Management Schema
CREATE SCHEMA IF NOT EXISTS user_mgmt;

-- Chat Schema
CREATE SCHEMA IF NOT EXISTS chat;

-- Document Schema
CREATE SCHEMA IF NOT EXISTS document;

-- Quiz Schema
CREATE SCHEMA IF NOT EXISTS quiz;

-- List schemas
\dn
```

#### Create Service Users

```sql
-- User Management Service User
CREATE USER user_mgmt_svc WITH PASSWORD 'secure_password_1';
GRANT ALL PRIVILEGES ON SCHEMA user_mgmt TO user_mgmt_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA user_mgmt TO user_mgmt_svc;
ALTER DEFAULT PRIVILEGES IN SCHEMA user_mgmt GRANT ALL ON TABLES TO user_mgmt_svc;

-- Chat Service User
CREATE USER chat_svc WITH PASSWORD 'secure_password_2';
GRANT ALL PRIVILEGES ON SCHEMA chat TO chat_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA chat TO chat_svc;
ALTER DEFAULT PRIVILEGES IN SCHEMA chat GRANT ALL ON TABLES TO chat_svc;

-- Document Service User
CREATE USER document_svc WITH PASSWORD 'secure_password_3';
GRANT ALL PRIVILEGES ON SCHEMA document TO document_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA document TO document_svc;
ALTER DEFAULT PRIVILEGES IN SCHEMA document GRANT ALL ON TABLES TO document_svc;

-- Quiz Service User
CREATE USER quiz_svc WITH PASSWORD 'secure_password_4';
GRANT ALL PRIVILEGES ON SCHEMA quiz TO quiz_svc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA quiz TO quiz_svc;
ALTER DEFAULT PRIVILEGES IN SCHEMA quiz GRANT ALL ON TABLES TO quiz_svc;

-- Verify
\du
```

#### Backup Database

```bash
# From app node
pg_dump -h <rds-endpoint> \
        -U postgres \
        -d platform_main \
        -F c \
        -f backup_$(date +%Y%m%d).dump

# Download backup
scp cloud-app1:backup_*.dump ./backups/
```

#### Restore Database

```bash
# Upload backup
scp backup_20241129.dump cloud-app1:~/

# SSH to app node
ssh cloud-app1

# Restore
pg_restore -h <rds-endpoint> \
           -U postgres \
           -d platform_main \
           -c \
           backup_20241129.dump
```

---

## Kafka Operations

### Accessing Kafka

```bash
# SSH to Kafka node
ssh cloud-kafka
```

### List Topics

```bash
/opt/kafka/bin/kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092
```

### Create Topic

```bash
/opt/kafka/bin/kafka-topics.sh \
  --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic my-new-topic
```

### Describe Topic

```bash
/opt/kafka/bin/kafka-topics.sh \
  --describe \
  --bootstrap-server localhost:9092 \
  --topic document.uploaded
```

### Produce Messages (Testing)

```bash
/opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic document.uploaded

# Type messages, press Ctrl+D to exit
```

### Consume Messages (Testing)

```bash
/opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic document.uploaded \
  --from-beginning
```

### Check Kafka Status

```bash
# Check if Kafka is running
sudo systemctl status kafka

# Check Zookeeper
sudo systemctl status zookeeper

# Kafka logs
tail -f /opt/kafka/logs/server.log

# Zookeeper logs
tail -f /opt/kafka/logs/zookeeper.log
```

### Restart Kafka

```bash
sudo systemctl restart zookeeper
sleep 10
sudo systemctl restart kafka
```

---

## S3 Operations

### List Buckets

```bash
aws s3 ls | grep cloud-learning-platform
```

### Upload File to Bucket

```bash
# User management bucket
aws s3 cp file.txt s3://$(terraform output -raw s3_user_management_bucket)/path/

# Document bucket
aws s3 cp document.pdf s3://$(terraform output -raw s3_document_bucket)/documents/
```

### Download File from Bucket

```bash
aws s3 cp s3://$(terraform output -raw s3_document_bucket)/path/file.txt ./
```

### List Bucket Contents

```bash
aws s3 ls s3://$(terraform output -raw s3_document_bucket)/ --recursive
```

### Sync Directory to S3

```bash
aws s3 sync ./local-dir s3://$(terraform output -raw s3_document_bucket)/backup/
```

---

## Monitoring

### Check Instance Status

```bash
# All instances
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=cloud-learning-platform" \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name,PrivateIpAddress,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

### Check System Resources

#### On Nginx Node

```bash
ssh cloud-nginx

# CPU and Memory
top

# Disk usage
df -h

# Network connections
netstat -tulpn | grep nginx

# Nginx status
sudo systemctl status nginx
curl localhost/health
```

#### On App Nodes

```bash
ssh cloud-app1

# Check Docker
docker ps
docker stats

# Disk usage
df -h

# Check logs
sudo tail -f /var/log/messages
```

#### On Kafka Node

```bash
ssh cloud-kafka

# Check services
sudo systemctl status kafka
sudo systemctl status zookeeper

# Disk usage (important for Kafka)
df -h
du -sh /var/lib/kafka-logs/*

# Memory usage
free -h

# Kafka metrics
/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

### Check RDS Status

```bash
aws rds describe-db-instances \
  --db-instance-identifier cloud-learning-platform-dev-postgres \
  --query 'DBInstances[0].[DBInstanceStatus,AllocatedStorage,DBInstanceClass]'
```

### Check Costs

```bash
# Current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Daily costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost
```

---

## Troubleshooting

### Instance Not Responding

```bash
# Check instance status
aws ec2 describe-instance-status --instance-ids <instance-id>

# Check system logs
aws ec2 get-console-output --instance-id <instance-id>

# Reboot instance
aws ec2 reboot-instances --instance-ids <instance-id>
```

### Docker Issues

```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check Docker logs
sudo journalctl -u docker -f

# Clean up unused containers/images
docker system prune -a
```

### Database Connection Issues

```bash
# Test from app node
telnet <rds-endpoint> 5432

# Check security group
aws ec2 describe-security-groups --group-ids <db-sg-id>

# Check RDS parameter group
aws rds describe-db-parameters \
  --db-parameter-group-name <param-group-name>
```

### Nginx Not Routing

```bash
ssh cloud-nginx

# Check Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Check upstream connectivity
curl http://<app1-private-ip>:8000/health

# Reload Nginx
sudo systemctl reload nginx
```

### Kafka Not Working

```bash
ssh cloud-kafka

# Check if ports are listening
sudo netstat -tulpn | grep 9092  # Kafka
sudo netstat -tulpn | grep 2181  # Zookeeper

# Check logs
tail -f /opt/kafka/logs/server.log

# Test connectivity from app node
ssh cloud-app1
telnet <kafka-private-ip> 9092
```

---

## Maintenance Tasks

### Update Terraform Configuration

```bash
# Make changes to .tf files
nano terraform/variables.tf

# Plan changes
terraform plan

# Apply changes
terraform apply
```

### Update EC2 Instances

```bash
# SSH to instance
ssh cloud-nginx

# Update packages
sudo yum update -y

# Reboot if needed
sudo reboot
```

### Rotate Database Password

```bash
# Update RDS password
aws rds modify-db-instance \
  --db-instance-identifier cloud-learning-platform-dev-postgres \
  --master-user-password 'NewSecurePassword123!' \
  --apply-immediately

# Update application configurations
# (In Phase 2, update environment variables in containers)
```

### Clean Up Old S3 Versions

```bash
# List versions
aws s3api list-object-versions \
  --bucket <bucket-name> \
  --prefix path/

# Delete old versions (automated by lifecycle policy)
# Or manually:
aws s3api delete-object \
  --bucket <bucket-name> \
  --key <object-key> \
  --version-id <version-id>
```

---

## Backup and Recovery

### Full Infrastructure Backup

```bash
# 1. Backup Terraform state
cp terraform/terraform.tfstate terraform/terraform.tfstate.backup.$(date +%Y%m%d)

# 2. Backup database
ssh cloud-app1
pg_dump -h <rds-endpoint> -U postgres -d platform_main -F c -f full_backup.dump
exit
scp cloud-app1:full_backup.dump ./backups/

# 3. Backup S3 buckets
aws s3 sync s3://user-management-storage-dev-cloud-learning-platform ./s3-backup/user-mgmt/
aws s3 sync s3://document-service-storage-dev-cloud-learning-platform ./s3-backup/documents/
aws s3 sync s3://quiz-service-storage-dev-cloud-learning-platform ./s3-backup/quiz/

# 4. Backup Kafka topics (optional)
ssh cloud-kafka
# Use Kafka MirrorMaker or export topics
```

### Disaster Recovery

```bash
# 1. Restore infrastructure
cd terraform
terraform apply -auto-approve

# 2. Restore database
scp ./backups/full_backup.dump cloud-app1:~/
ssh cloud-app1
pg_restore -h <rds-endpoint> -U postgres -d platform_main -c full_backup.dump

# 3. Restore S3 data
aws s3 sync ./s3-backup/user-mgmt/ s3://<user-mgmt-bucket>/
aws s3 sync ./s3-backup/documents/ s3://<document-bucket>/
aws s3 sync ./s3-backup/quiz/ s3://<quiz-bucket>/
```

---

## Security Best Practices

### Rotate SSH Keys

```bash
# Create new key pair
aws ec2 create-key-pair --key-name new-key --query 'KeyMaterial' --output text > new-key.pem
chmod 400 new-key.pem

# Update instances (requires re-creation)
# Update terraform.tfvars
ec2_key_name = "new-key"

# Apply
terraform apply
```

### Update Security Groups

```bash
# Get your current IP
MY_IP=$(curl -s ifconfig.me)

# Update Terraform
allowed_ssh_cidr_blocks = ["$MY_IP/32"]

# Apply
terraform apply
```

### Audit Access Logs

```bash
# Check who accessed Nginx
ssh cloud-nginx
sudo grep "GET\|POST\|PUT\|DELETE" /var/log/nginx/access.log | tail -100

# Check SSH logins
sudo lastlog
sudo last
```

---

## Cost Optimization

### Stop Instances Schedule

Create a cron job or use AWS Lambda to stop instances:

```bash
# Stop at 6 PM
0 18 * * * aws ec2 stop-instances --instance-ids <ids>

# Start at 8 AM
0 8 * * * aws ec2 start-instances --instance-ids <ids>
```

### Monitor Costs Daily

```bash
# Create alias in ~/.bashrc
alias aws-cost='aws ce get-cost-and-usage --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) --granularity MONTHLY --metrics BlendedCost'

# Run daily
aws-cost
```

---

## Phase 2 Preparation

### Install Container Registry (ECR)

```bash
# Create ECR repositories
aws ecr create-repository --repository-name cloud-platform/chat-service
aws ecr create-repository --repository-name cloud-platform/user-management
aws ecr create-repository --repository-name cloud-platform/document-service
aws ecr create-repository --repository-name cloud-platform/quiz-service

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### Prepare Docker Compose Files

```bash
# On app nodes
ssh cloud-app1
cd /opt/app

# Create docker-compose.yml (will be done in Phase 2)
```

---

## Useful Commands Cheat Sheet

```bash
# Terraform
terraform init              # Initialize
terraform plan              # Preview changes
terraform apply             # Apply changes
terraform destroy           # Destroy all
terraform output            # Show outputs
terraform state list        # List resources
terraform fmt               # Format files
terraform validate          # Validate syntax

# AWS EC2
aws ec2 describe-instances  # List instances
aws ec2 start-instances     # Start instances
aws ec2 stop-instances      # Stop instances
aws ec2 reboot-instances    # Reboot instances

# AWS RDS
aws rds describe-db-instances
aws rds stop-db-instance
aws rds start-db-instance

# AWS S3
aws s3 ls                   # List buckets
aws s3 cp                   # Copy file
aws s3 sync                 # Sync directory

# Kafka
kafka-topics.sh --list
kafka-topics.sh --create
kafka-console-producer.sh
kafka-console-consumer.sh

# PostgreSQL
psql -h <host> -U <user> -d <db>
\l                          # List databases
\dn                         # List schemas
\dt                         # List tables
\q                          # Quit

# Docker
docker ps                   # List containers
docker logs <container>     # View logs
docker exec -it <container> bash  # Shell into container
docker-compose up -d        # Start services
docker-compose down         # Stop services
```

---

**Keep this guide handy for daily operations!**

