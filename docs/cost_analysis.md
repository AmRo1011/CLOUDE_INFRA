# Cost Analysis - Cloud Learning Platform (Dev Environment)

## Monthly Cost Breakdown

### Compute (EC2)
| Resource | Type | Units | Cost/Unit | Monthly Cost |
|----------|------|-------|-----------|--------------|
| Nginx Gateway | t3.micro | 1 | $7.50/month | **$7.50** |
| App Node 1 | t3.small | 1 | $15.00/month | **$15.00** |
| App Node 2 | t3.small | 1 | $15.00/month | **$15.00** |
| Kafka Node | t3.small | 1 | $15.00/month | **$15.00** |
| **Subtotal** | | | | **$52.50** |

### Storage (EBS)
| Resource | Type | Size | Cost/GB | Monthly Cost |
|----------|------|------|---------|--------------|
| Root volumes (4x) | gp3 | 20GB each | $0.08/GB | **$6.40** |
| Kafka data volume | gp3 | 30GB | $0.08/GB | **$2.40** |
| **Subtotal** | | | | **$8.80** |

### Database (RDS)
| Resource | Type | Storage | Monthly Cost |
|----------|------|---------|--------------|
| PostgreSQL | db.t3.micro | 20GB gp3 | **$12.50** |

### Storage (S3)
| Resource | Estimated Size | Monthly Cost |
|----------|----------------|--------------|
| 3 Buckets (user-mgmt, document, quiz) | 5GB total | **$0.12** |
| Requests (PUT/GET) | ~10k requests | **$0.05** |
| **Subtotal** | | **$0.17** |

### Networking
| Resource | Monthly Cost |
|----------|--------------|
| NAT Gateway (1x) | **$32.40** |
| Data Transfer (estimated 10GB) | **$0.90** |
| **Subtotal** | **$33.30** |

### Data Transfer
| Type | Estimated Volume | Cost/GB | Monthly Cost |
|------|------------------|---------|--------------|
| EC2 to Internet | 5GB | $0.09 | **$0.45** |
| Inter-AZ | 5GB | $0.01 | **$0.05** |
| **Subtotal** | | | **$0.50** |

---

## **Total Monthly Cost: ~$107.77**

## ⚠️ Cost Optimization Strategies to Meet $50 Budget

### Critical Reductions

#### Option 1: Eliminate NAT Gateway (-$32.40)
- **Remove NAT Gateway completely**
- App instances won't have internet access
- Must use VPC endpoints for AWS services (S3, RDS)
- Or use bastion host for proxy
- **New Total: ~$75.37**

#### Option 2: Combine App Nodes (-$15.00)
- Run all services on a single t3.medium instance ($30/month)
- Still maintains containerization
- Reduces complexity
- **Savings: $15-20**

#### Option 3: Use t4g (ARM) instances (-$15-20)
- t4g.micro instead of t3.micro (~20% cheaper)
- t4g.small instead of t3.small (~20% cheaper)
- Requires ARM-compatible Docker images
- **Savings: ~$10-12/month**

#### Option 4: Stop Instances When Not in Use
- **Stop EC2 instances during non-working hours**
- Only pay for EBS storage when stopped
- With 12 hours/day usage: **50% savings on EC2 = ~$26 saved**
- **Estimated: ~$55-60/month**

### Recommended Budget-Conscious Configuration

```hcl
# Optimized for ~$45-50/month
nginx_instance_type = "t4g.micro"    # $6/month
app_instance_type   = "t4g.medium"   # $24/month (single node)
kafka_instance_type = "t4g.small"    # $12/month
db_instance_class   = "db.t4g.micro" # $10/month

# Remove NAT Gateway or use only during testing
enable_nat_gateway = false

# Reduce storage
kafka_ebs_volume_size = 20 # Instead of 50GB
db_allocated_storage  = 10 # Instead of 20GB
```

**Optimized Total: ~$48-52/month**

### Additional Cost-Saving Tips

1. **Use AWS Free Tier** (First 12 months)
   - 750 hours/month of t2.micro/t3.micro EC2
   - 20GB RDS storage
   - 5GB S3 storage
   - **Potential savings: ~$20-30/month**

2. **Schedule Automated Start/Stop**
   ```bash
   # Stop instances at night
   aws ec2 stop-instances --instance-ids i-xxx
   
   # Start in morning
   aws ec2 start-instances --instance-ids i-xxx
   ```

3. **Use Reserved Instances** (Not applicable for short-term project)

4. **Delete Resources After Testing**
   - Use `terraform destroy` when not actively developing
   - Rebuild when needed (~5-10 minutes)

5. **Monitor with CloudWatch Alarms**
   - Set billing alerts at $30, $40, $50
   - Track usage daily

---

## Cost by Service

| Service | Monthly Cost |
|---------|--------------|
| Compute (EC2) | $52.50 |
| Storage (EBS) | $8.80 |
| Database (RDS) | $12.50 |
| Storage (S3) | $0.17 |
| Networking (NAT) | $33.30 |
| **Total** | **$107.77** |

---

## Phase 2 & 3 Cost Considerations

### Additional Costs Expected:
- **ECR (Container Registry)**: $0.10/GB storage (~$1-2/month)
- **CloudWatch Logs**: $0.50/GB ingested (~$2-5/month)
- **Application Load Balancer**: $16.20/month (if replacing Nginx)
- **Additional ECS/Fargate**: $20-50/month (if using managed containers)

### High-Availability Configuration Cost:
- **3 Kafka brokers**: +$30/month
- **3 Zookeeper nodes**: +$22/month
- **Multi-AZ RDS**: +$12/month
- **2 NAT Gateways**: +$32/month
- **Load balancer**: +$16/month
- **Production Total**: ~$250-300/month

---

## Learner Lab Considerations

AWS Learner Lab typically provides:
- **$100 credit** for the course
- **4-hour session limit** (instances stop automatically)
- **Limited IAM permissions**
- **No cost for stopped instances** (only storage)

### Optimization for Learner Lab:
1. Start lab session only when actively working
2. Terraform apply at start of session
3. Work for ~3 hours
4. Terraform destroy before session ends
5. Commit code to Git for next session

**Effective cost: ~$0-5 per 4-hour session**

---

## Monitoring Commands

```bash
# Get current month costs
aws ce get-cost-and-usage \
    --time-period Start=2024-12-01,End=2024-12-31 \
    --granularity MONTHLY \
    --metrics BlendedCost

# List running instances with costs
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name]'
```

