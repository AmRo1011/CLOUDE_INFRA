# Quick Reference Guide - Cloud Learning Platform

## 🚀 Quick Commands

### Deploy Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Check Status
```bash
./scripts/status.sh
```

### Destroy Infrastructure
```bash
./scripts/destroy.sh
```

---

## 📡 Access Information

### Endpoints
```bash
# API Gateway
http://<nginx-public-ip>

# Health Check
curl http://<nginx-public-ip>/health

# Service Endpoints
/api/chat/*         - Chat Service
/api/users/*        - User Management
/api/auth/*         - Authentication
/api/documents/*    - Document Service
/api/quiz/*         - Quiz Service
```

### SSH Access
```bash
# Nginx (public)
ssh -i key.pem ec2-user@<nginx-public-ip>

# App nodes (through bastion)
ssh -i key.pem -J ec2-user@<nginx-ip> ec2-user@<app-private-ip>

# Kafka node (through bastion)
ssh -i key.pem -J ec2-user@<nginx-ip> ec2-user@<kafka-private-ip>
```

---

## 🗄️ Database Commands

### Connect to RDS
```bash
psql -h <rds-endpoint> -U postgres -d platform_main
```

### Create Schemas
```sql
CREATE SCHEMA user_mgmt;
CREATE SCHEMA chat;
CREATE SCHEMA document;
CREATE SCHEMA quiz;
```

### List Schemas
```sql
\dn
```

---

## 📦 Kafka Commands

### List Topics
```bash
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Create Topic
```bash
/opt/kafka/bin/kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic my-topic
```

### Produce Messages
```bash
/opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic document.uploaded
```

### Consume Messages
```bash
/opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic document.uploaded \
  --from-beginning
```

---

## 🪣 S3 Commands

### List Buckets
```bash
aws s3 ls | grep cloud-learning-platform
```

### Upload File
```bash
aws s3 cp file.txt s3://bucket-name/path/
```

### Download File
```bash
aws s3 cp s3://bucket-name/path/file.txt ./
```

### Sync Directory
```bash
aws s3 sync ./local-dir s3://bucket-name/backup/
```

---

## 🖥️ EC2 Commands

### List Instances
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=cloud-learning-platform" \
  --query 'Reservations[].Instances[].[InstanceId,State.Name,PrivateIpAddress,PublicIpAddress]' \
  --output table
```

### Stop Instances
```bash
aws ec2 stop-instances --instance-ids <instance-id>
```

### Start Instances
```bash
aws ec2 start-instances --instance-ids <instance-id>
```

### Reboot Instance
```bash
aws ec2 reboot-instances --instance-ids <instance-id>
```

---

## 💵 Cost Commands

### Current Month Cost
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### Daily Costs (Last 7 Days)
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost
```

---

## 🔍 Terraform Commands

### Initialize
```bash
terraform init
```

### Format Code
```bash
terraform fmt -recursive
```

### Validate
```bash
terraform validate
```

### Plan Changes
```bash
terraform plan -out=tfplan
```

### Apply Changes
```bash
terraform apply tfplan
```

### Destroy All
```bash
terraform destroy
```

### Show Resources
```bash
terraform state list
```

### Show Outputs
```bash
terraform output
```

### Refresh State
```bash
terraform refresh
```

---

## 🔧 Troubleshooting

### Check Instance Logs
```bash
ssh ec2-user@<ip>
sudo cat /var/log/cloud-init-output.log
sudo cat /var/log/user-data-complete.log
```

### Check Service Status
```bash
# Nginx
sudo systemctl status nginx

# Docker
sudo systemctl status docker
docker ps

# Kafka
sudo systemctl status kafka

# Zookeeper
sudo systemctl status zookeeper
```

### Test Connectivity
```bash
# From app node to RDS
telnet <rds-endpoint> 5432

# From app node to Kafka
telnet <kafka-ip> 9092

# From nginx to app
curl http://<app-ip>:8000/health
```

### Restart Services
```bash
# Nginx
sudo systemctl restart nginx

# Docker
sudo systemctl restart docker

# Kafka
sudo systemctl restart zookeeper
sleep 10
sudo systemctl restart kafka
```

---

## 📊 Monitoring

### Check Disk Usage
```bash
df -h
```

### Check Memory
```bash
free -h
```

### Check CPU
```bash
top
```

### Check Network
```bash
netstat -tulpn
```

### Docker Stats
```bash
docker stats
```

---

## 🔐 Security

### Update Security Group
```bash
# Get your IP
MY_IP=$(curl -s ifconfig.me)

# Update terraform.tfvars
allowed_ssh_cidr_blocks = ["$MY_IP/32"]

# Apply
terraform apply
```

### Rotate Database Password
```bash
aws rds modify-db-instance \
  --db-instance-identifier <db-id> \
  --master-user-password 'NewPassword123!' \
  --apply-immediately
```

---

## 📁 Important Files

### Configuration
- `terraform/terraform.tfvars` - Your configuration
- `terraform/main.tf` - Main infrastructure
- `terraform/variables.tf` - Variable definitions

### Documentation
- `README.md` - Main documentation
- `docs/operations.md` - Detailed operations
- `docs/cost_analysis.md` - Cost information
- `PROJECT_SUMMARY.md` - Project overview

### Scripts
- `scripts/deploy.sh` - Deploy infrastructure
- `scripts/destroy.sh` - Destroy infrastructure
- `scripts/status.sh` - Check status

---

## 🆘 Emergency Procedures

### Infrastructure Not Responding
```bash
# 1. Check AWS Console
# 2. Check instance status
aws ec2 describe-instance-status --instance-ids <id>

# 3. Reboot if needed
aws ec2 reboot-instances --instance-ids <id>

# 4. If all else fails, destroy and recreate
terraform destroy
terraform apply
```

### Out of Budget
```bash
# Stop all instances immediately
aws ec2 stop-instances --instance-ids $(terraform output -json | jq -r '.*.value')

# Or destroy everything
terraform destroy
```

### Lost SSH Access
```bash
# Check security group
aws ec2 describe-security-groups --group-ids <sg-id>

# Update rules
terraform apply
```

---

## 📞 Support Resources

### AWS Documentation
- https://docs.aws.amazon.com/

### Terraform Documentation
- https://www.terraform.io/docs

### Project Documentation
- [README.md](README.md)
- [docs/operations.md](docs/operations.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)

---

## ⚡ Tips & Tricks

### Speed Up Deployment
```bash
# Parallel resource creation (Terraform does this automatically)
terraform apply -parallelism=10
```

### Save Money
```bash
# Stop instances when not in use
aws ec2 stop-instances --instance-ids $(terraform state show aws_instance.* | grep "id " | awk '{print $3}')

# Use Learner Lab - destroy after each session
terraform destroy -auto-approve
```

### Quick Health Check
```bash
# One-liner to check all services
curl -s http://<nginx-ip>/health && echo "✅ Nginx OK" || echo "❌ Nginx Down"
```

### Backup Everything
```bash
# Database
pg_dump -h <rds-endpoint> -U postgres -d platform_main > backup.sql

# S3 buckets
aws s3 sync s3://bucket-name ./s3-backup/

# Terraform state
cp terraform/terraform.tfstate terraform/terraform.tfstate.backup
```

---

**Keep this guide handy for quick reference! 📖**

