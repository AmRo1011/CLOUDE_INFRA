# Getting Started - Cloud Learning Platform

## 📋 Pre-Deployment Checklist

Before you begin, make sure you have:

- [ ] AWS Account (or Learner Lab access)
- [ ] AWS CLI installed and configured
- [ ] Terraform >= 1.5.0 installed
- [ ] Git installed
- [ ] Basic understanding of AWS services
- [ ] 30-60 minutes for initial setup

---

## 🎯 Step-by-Step Guide

### Step 1: Clone Repository (2 minutes)

```bash
# Clone the repository
git clone <repository-url>
cd CLOUDE_INFRA

# Verify structure
ls -la
```

**Expected output:**
```
README.md
terraform/
scripts/
docs/
```

---

### Step 2: Configure AWS Credentials (5 minutes)

#### Option A: AWS CLI Configuration
```bash
aws configure
```

Enter when prompted:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

#### Option B: Learner Lab
```bash
# Copy credentials from Learner Lab
# Set as environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_SESSION_TOKEN="your-token"
export AWS_DEFAULT_REGION="us-east-1"
```

**Verify:**
```bash
aws sts get-caller-identity
```

---

### Step 3: Create EC2 Key Pair (3 minutes)

#### Option A: AWS Console
1. Go to EC2 Console
2. Click "Key Pairs" in left menu
3. Click "Create Key Pair"
4. Name: `cloud-platform-key`
5. Type: RSA
6. Format: `.pem`
7. Download and save securely

#### Option B: AWS CLI
```bash
aws ec2 create-key-pair \
  --key-name cloud-platform-key \
  --query 'KeyMaterial' \
  --output text > cloud-platform-key.pem

chmod 400 cloud-platform-key.pem
```

**Important:** Keep this file safe! You'll need it for SSH access.

---

### Step 4: Configure Terraform Variables (5 minutes)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
# Required Changes
ec2_key_name = "cloud-platform-key"  # Your key pair name
db_password  = "YourSecurePassword123!"  # Strong password (min 8 chars)

# Optional Changes (defaults are fine)
aws_region = "us-east-1"
project_name = "cloud-learning-platform"
environment = "dev"

# Instance types (cost-optimized)
nginx_instance_type = "t3.micro"
app_instance_type = "t3.small"
kafka_instance_type = "t3.small"

# Database
db_instance_class = "db.t3.micro"
db_username = "postgres"
```

**Security Note:** Never commit `terraform.tfvars` to git!

---

### Step 5: Initialize Terraform (2 minutes)

```bash
# Still in terraform/ directory
terraform init
```

**Expected output:**
```
Terraform has been successfully initialized!
```

**What this does:**
- Downloads AWS provider
- Initializes modules
- Prepares backend

---

### Step 6: Validate Configuration (1 minute)

```bash
terraform validate
```

**Expected output:**
```
Success! The configuration is valid.
```

**If errors:** Check your `terraform.tfvars` syntax.

---

### Step 7: Preview Infrastructure (3 minutes)

```bash
terraform plan
```

**Review the plan carefully!**

Look for:
- ✅ Number of resources to create (~30-40)
- ✅ Instance types match your budget
- ✅ No errors or warnings
- ❌ Any unexpected resources

**Sample output:**
```
Plan: 35 to add, 0 to change, 0 to destroy.
```

---

### Step 8: Deploy Infrastructure (15 minutes)

```bash
terraform apply
```

Type `yes` when prompted.

**What happens:**
1. Creates VPC and networking (2 min)
2. Creates security groups (1 min)
3. Creates RDS database (8 min) ⏰ Slowest part
4. Creates EC2 instances (3 min)
5. Creates S3 buckets (1 min)

**☕ Grab coffee while RDS deploys!**

---

### Step 9: Save Important Information (2 minutes)

After successful deployment:

```bash
# Save outputs to file
terraform output > ../deployment_info.txt

# View connection info
terraform output connection_info
```

**Save these values:**
- Nginx Public IP
- RDS Endpoint
- Kafka Private IP
- S3 Bucket Names

---

### Step 10: Verify Deployment (5 minutes)

#### Test 1: Check Infrastructure Status
```bash
cd ..
./scripts/status.sh
```

#### Test 2: Test Nginx Health
```bash
NGINX_IP=$(cd terraform && terraform output -raw nginx_public_ip)
curl http://$NGINX_IP/health
```

**Expected:** `healthy`

#### Test 3: SSH to Nginx
```bash
ssh -i cloud-platform-key.pem ec2-user@$NGINX_IP
```

**Inside instance:**
```bash
# Check Docker
docker --version

# Check Nginx
sudo systemctl status nginx

# Exit
exit
```

---

### Step 11: Setup Database Schemas (5 minutes)

#### Connect to app node
```bash
ssh -i cloud-platform-key.pem -J ec2-user@$NGINX_IP ec2-user@<APP1_PRIVATE_IP>
```

#### Install PostgreSQL client
```bash
sudo yum install postgresql -y
```

#### Connect to RDS
```bash
RDS_ENDPOINT="<from terraform output>"
psql -h $RDS_ENDPOINT -U postgres -d platform_main
# Enter password when prompted
```

#### Create schemas
```sql
CREATE SCHEMA user_mgmt;
CREATE SCHEMA chat;
CREATE SCHEMA document;
CREATE SCHEMA quiz;

-- Verify
\dn

-- Exit
\q
```

---

### Step 12: Verify Kafka (5 minutes)

#### SSH to Kafka node
```bash
ssh -i cloud-platform-key.pem -J ec2-user@$NGINX_IP ec2-user@<KAFKA_PRIVATE_IP>
```

#### Check Kafka status
```bash
sudo systemctl status kafka
sudo systemctl status zookeeper
```

#### List topics
```bash
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Expected topics:**
- document.uploaded
- document.processed
- notes.generated
- quiz.requested
- quiz.generated
- chat.message
- (and others)

---

## ✅ Deployment Complete!

### What You Now Have:

- ✅ VPC with public and private subnets
- ✅ Nginx gateway (public access)
- ✅ 2 Application nodes (Docker-ready)
- ✅ Kafka + Zookeeper cluster
- ✅ PostgreSQL database with schemas
- ✅ 3 S3 buckets (isolated per service)
- ✅ Security groups configured
- ✅ All services networking properly

---

## 🎯 Next Steps

### Immediate (Phase 1)
1. ✅ Test all connections
2. ✅ Verify Kafka topics
3. ✅ Check database schemas
4. ✅ Document any issues

### Phase 2: Microservices (Next Deadline)
1. Containerize services
2. Deploy to EC2 nodes
3. Configure service mesh
4. Test end-to-end

### Phase 3: Observability (Final)
1. Setup monitoring
2. Configure logging
3. Add alerting
4. Performance tuning

---

## 💰 Cost Management

### Daily Monitoring
```bash
# Check costs daily
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### Budget Alerts
Set up in AWS Console:
1. Go to Billing → Budgets
2. Create budget: $50/month
3. Add email alerts at 80%, 100%

### Cost Saving Tips

#### Strategy 1: Stop Instances When Not Using
```bash
# Stop (keeps data, stops charges)
aws ec2 stop-instances --instance-ids <ids>

# Start when needed
aws ec2 start-instances --instance-ids <ids>
```

#### Strategy 2: Learner Lab Workflow
```bash
# Start of session
terraform apply

# End of session
terraform destroy

# Commit code to Git before destroying!
```

#### Strategy 3: Scheduled Shutdown
```bash
# Cron job to stop at 6 PM
0 18 * * * aws ec2 stop-instances --instance-ids $(cat instance_ids.txt)
```

---

## 🆘 Troubleshooting

### Issue: Terraform Apply Fails

**Error:** `InvalidKeyPair.NotFound`
```bash
# Solution: Create the key pair first
aws ec2 create-key-pair --key-name cloud-platform-key
```

**Error:** `Insufficient Quota`
```bash
# Solution: Check service limits
aws service-quotas list-service-quotas --service-code ec2
# Request quota increase if needed
```

**Error:** `UnauthorizedOperation`
```bash
# Solution: Check AWS credentials
aws sts get-caller-identity
aws configure
```

### Issue: Can't SSH to Instances

**Problem:** Connection timeout
```bash
# Check security group
aws ec2 describe-security-groups --group-ids <sg-id>

# Update your IP
MY_IP=$(curl -s ifconfig.me)
# Edit terraform.tfvars:
allowed_ssh_cidr_blocks = ["$MY_IP/32"]

terraform apply
```

### Issue: High Costs

**Problem:** Unexpected charges
```bash
# Check what's running
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running"

# Check NAT Gateway (expensive!)
aws ec2 describe-nat-gateways

# Stop everything
terraform destroy
```

---

## 📚 Resources

### Documentation
- [README.md](README.md) - Full documentation
- [docs/operations.md](docs/operations.md) - Daily operations
- [docs/cost_analysis.md](docs/cost_analysis.md) - Cost details
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command reference

### AWS Resources
- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS Pricing Calculator](https://calculator.aws/)

### Terraform Resources
- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

## 🎓 Learning Path

### Beginner (Week 1)
- [ ] Deploy infrastructure
- [ ] SSH to instances
- [ ] Understand VPC basics
- [ ] Practice terraform commands

### Intermediate (Week 2)
- [ ] Modify security groups
- [ ] Add monitoring
- [ ] Database operations
- [ ] Kafka basics

### Advanced (Week 3+)
- [ ] Scale to HA
- [ ] Implement auto-scaling
- [ ] Add load balancer
- [ ] Multi-region setup

---

## ✨ Tips for Success

### 1. Document Everything
- Keep notes of what works
- Screenshot important configs
- Save all outputs

### 2. Test in Isolation
- Deploy one module at a time first
- Test each component
- Then deploy full stack

### 3. Use Version Control
```bash
git add .
git commit -m "Working configuration"
git push
```

### 4. Regular Backups
```bash
# Database
pg_dump > backup.sql

# Terraform state
cp terraform.tfstate terraform.tfstate.backup

# S3 data
aws s3 sync s3://bucket ./backup/
```

### 5. Monitor Costs
- Check AWS Console daily
- Set up billing alerts
- Use cost explorer

---

## 🎉 Congratulations!

You've successfully deployed a production-grade AWS infrastructure!

**What's Next?**
1. Explore the infrastructure
2. Customize for your needs
3. Move to Phase 2 (Microservices)
4. Share with your team

**Need Help?**
- Check [docs/operations.md](docs/operations.md)
- Review [README.md](README.md)
- Ask your instructor/TA

---

**Happy Cloud Computing! ☁️**

