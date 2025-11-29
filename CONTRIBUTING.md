# Contributing to Cloud Learning Platform

## Team Members

This is a collaborative project for CSE363 Cloud Computing Course.

**Team Members:**
- [Add your names here]

## Development Workflow

### 1. Branch Strategy

```bash
# Main branch - stable infrastructure
main

# Development branch - active development
dev

# Feature branches - specific features
feature/vpc-enhancement
feature/monitoring-setup
```

### 2. Making Changes

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes to Terraform files
# ... edit files ...

# Test locally
cd terraform
terraform init
terraform plan

# Commit with descriptive message
git add .
git commit -m "Add: Enhanced VPC security groups"

# Push to remote
git push origin feature/your-feature-name

# Create pull request for review
```

### 3. Commit Message Convention

```
Type: Brief description

Detailed description if needed

Type can be:
- Add: New feature or resource
- Fix: Bug fix
- Update: Modify existing resource
- Docs: Documentation changes
- Refactor: Code restructuring
- Test: Add or modify tests
```

**Examples:**
```
Add: RDS Multi-AZ configuration option

Added variable to enable Multi-AZ deployment for RDS
in production environments. Defaults to false for dev.

---

Fix: Security group ingress rules for Kafka

Corrected Kafka security group to allow connections
from app-sg on port 9092.

---

Docs: Update cost analysis with latest pricing

Updated cost_analysis.md with December 2024 AWS pricing
for t3 and t4g instance types.
```

### 4. Code Review Checklist

Before submitting pull request:

- [ ] Terraform code formatted (`terraform fmt`)
- [ ] Terraform validation passed (`terraform validate`)
- [ ] Plan executed successfully (`terraform plan`)
- [ ] No sensitive data in code (passwords, keys)
- [ ] Documentation updated (if applicable)
- [ ] Cost impact analyzed
- [ ] Security implications considered
- [ ] Comments added for complex logic

### 5. Testing Changes

```bash
# Always test in dev environment first
cd terraform

# Initialize
terraform init

# Plan changes
terraform plan -out=test.tfplan

# Review plan carefully
# Check estimated costs

# Apply in dev
terraform apply test.tfplan

# Verify functionality
./scripts/status.sh

# If successful, clean up
terraform destroy
```

## Project Structure Guidelines

### Terraform Modules

Each module should:
- Be self-contained and reusable
- Have clear input variables
- Provide useful outputs
- Include inline comments
- Follow naming conventions

### Documentation

Keep updated:
- `README.md` - Main project documentation
- `docs/` - Detailed guides and architecture
- Inline comments in Terraform files
- Module README files (optional but recommended)

### Scripts

Helper scripts in `scripts/`:
- Use bash for portability
- Include error handling (`set -e`)
- Add colored output for clarity
- Comment complex sections

## Cost Management

### Before Committing Changes

1. **Estimate cost impact:**
   ```bash
   # Use AWS Pricing Calculator
   # Or terraform-cost-estimation
   ```

2. **Document in pull request:**
   - Current monthly cost
   - New monthly cost
   - Justification for increase

3. **Optimize when possible:**
   - Use spot instances for dev
   - Right-size resources
   - Enable auto-shutdown

### Cost Alerts

Set up billing alerts:
```bash
aws budgets create-budget \
    --account-id <account-id> \
    --budget file://budget.json
```

## Security Best Practices

### Never Commit

❌ Passwords or secrets  
❌ Private keys (.pem, .ppk)  
❌ AWS access keys  
❌ terraform.tfvars with real values  

### Always Use

✅ terraform.tfvars.example templates  
✅ Sensitive variables with `sensitive = true`  
✅ .gitignore for secrets  
✅ Environment variables for credentials  

### Code Review Focus

- Security group rules (least privilege)
- Public vs private subnets
- Encryption settings
- IAM permissions (when available)

## Communication

### Daily Standups (Recommended)

Share:
1. What I did yesterday
2. What I'm working on today
3. Any blockers

### Issue Tracking

Use GitHub Issues for:
- Bug reports
- Feature requests
- Questions
- Task assignments

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Infrastructure change

## Testing Done
- [ ] terraform plan
- [ ] terraform apply (dev)
- [ ] Manual testing
- [ ] Cost analysis

## Cost Impact
Current: $X/month
New: $Y/month
Difference: $Z/month

## Screenshots (if applicable)
Add screenshots of architecture or AWS console

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] No sensitive data committed
- [ ] Tested in dev environment
```

## Getting Help

### Resources

1. **AWS Documentation**
   - https://docs.aws.amazon.com/

2. **Terraform Documentation**
   - https://www.terraform.io/docs

3. **Course Materials**
   - CSE363 lecture slides
   - Lab materials

4. **Team Communication**
   - Team chat/Discord
   - Email
   - Office hours

### Common Issues

See [Troubleshooting](README.md#troubleshooting) in main README.

## Phase Milestones

### Phase 1: Infrastructure (Current)
- ✅ VPC and networking
- ✅ Security groups
- ✅ EC2 instances
- ✅ RDS database
- ✅ S3 buckets
- ✅ Kafka setup

### Phase 2: Microservices
- [ ] Containerize services
- [ ] Deploy to EC2
- [ ] Configure service mesh
- [ ] Implement API gateway
- [ ] Set up CI/CD

### Phase 3: Observability
- [ ] CloudWatch integration
- [ ] Distributed tracing
- [ ] Log aggregation
- [ ] Metrics dashboards
- [ ] Alerting

## License

Educational project for CSE363 Cloud Computing Course.

---

**Happy Coding! 🚀**

