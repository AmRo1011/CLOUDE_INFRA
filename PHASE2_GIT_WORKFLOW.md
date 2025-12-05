# Phase 2 Git Workflow Guide

## Overview

This document describes the Git workflow for Phase 2 development. The goal is to enable 3 team members to work in parallel without conflicts while keeping Phase 1 infrastructure completely stable.

## Branch Strategy

### Main Branches

```
main (or master)
  └── phase-1-final (tag)
        └── phase-2 (long-lived branch for all Phase 2 work)
              ├── phase-2/user-mgmt-service (Person A)
              ├── phase-2/document-quiz-services (Person B)
              └── phase-2/chat-kafka-and-deploy (Person C)
```

### Branch Naming Convention

- Feature branches: `phase-2/<feature-name>`
- Hotfix branches: `phase-2/hotfix/<issue>`

## Getting Started

### 1. Tag Phase 1 Completion

```bash
# Ensure you're on the main branch with all Phase 1 work
git checkout main
git pull origin main

# Tag the Phase 1 final state
git tag -a phase-1-final -m "Phase 1 Infrastructure Complete"
git push origin phase-1-final
```

### 2. Create Phase 2 Branch

```bash
# Create phase-2 branch from the tag
git checkout -b phase-2 phase-1-final
git push -u origin phase-2
```

### 3. Create Your Feature Branch

```bash
# Make sure you're on phase-2
git checkout phase-2
git pull origin phase-2

# Create your feature branch
# Person A:
git checkout -b phase-2/user-mgmt-service

# Person B:
git checkout -b phase-2/document-quiz-services

# Person C:
git checkout -b phase-2/chat-kafka-and-deploy
```

## Team Assignments

### Person A - User Management & RBAC

**Branch:** `phase-2/user-mgmt-service`

**Responsibilities:**
- `services/user-mgmt/` - Full implementation
- `deploy/nginx/` - Auth-related location blocks
- `docs/api_contracts_phase2.md` - Auth/Users API section

**Files to Own:**
```
services/user-mgmt/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── utils/
├── tests/
├── Dockerfile
└── requirements.txt
```

### Person B - Document & Quiz Services

**Branch:** `phase-2/document-quiz-services`

**Responsibilities:**
- `services/document/` - Full implementation
- `services/quiz/` - Full implementation
- `docs/kafka_contracts_phase2.md` - Event schemas
- `docs/api_contracts_phase2.md` - Document/Quiz API sections

**Files to Own:**
```
services/document/
services/quiz/
```

### Person C - Chat & Deployment

**Branch:** `phase-2/chat-kafka-and-deploy`

**Responsibilities:**
- `services/chat/` - Full implementation
- `deploy/` - Docker Compose files, deployment scripts
- `.github/workflows/` - CI/CD pipelines
- Coordinate env vars with A & B

**Files to Own:**
```
services/chat/
deploy/docker-compose.*.yml
deploy/scripts/
.github/workflows/
```

## Golden Rules

### DO NOT MODIFY (Phase 1 Files)

These files are **OFF LIMITS** - no modifications allowed:

```
terraform/**           # All Terraform infrastructure code
scripts/deploy.sh      # Phase 1 deploy script
scripts/destroy.sh     # Phase 1 destroy script
scripts/status.sh      # Phase 1 status script
docs/architecture_diagram.md
docs/cost_analysis.md
docs/database_decision.md
docs/operations.md
README.md             # (Phase 1 content - only append Phase 2 section at end)
PROJECT_SUMMARY.md    # (Phase 1 content - only append Phase 2 section at end)
```

### ONLY ADD NEW FILES

All Phase 2 work should be in new directories:
- `services/` - New microservice code
- `deploy/` - New deployment configurations
- `.github/workflows/` - New CI/CD pipelines
- `docs/phase2_*.md` - New Phase 2 documentation

## Daily Workflow

### Starting Work

```bash
# Update your feature branch with latest phase-2
git checkout phase-2
git pull origin phase-2
git checkout phase-2/your-feature
git merge phase-2
```

### Committing Changes

```bash
# Stage your changes
git add services/your-service/

# Commit with descriptive message
git commit -m "feat(user-mgmt): add JWT authentication endpoint"

# Push to your feature branch
git push origin phase-2/your-feature
```

### Commit Message Format

Follow conventional commits:
- `feat(service): description` - New feature
- `fix(service): description` - Bug fix
- `docs(service): description` - Documentation
- `test(service): description` - Tests
- `refactor(service): description` - Code refactoring

Examples:
```
feat(user-mgmt): implement user registration endpoint
fix(chat): handle Kafka connection timeout
docs(api): add quiz endpoints documentation
test(document): add upload service unit tests
```

## Pull Request Process

### Creating a PR

1. Push your feature branch
2. Create PR to `phase-2` branch (NOT main!)
3. Fill in PR template
4. Request review from at least one teammate

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Tests

## Service(s) Affected
- [ ] User Management
- [ ] Chat
- [ ] Document
- [ ] Quiz
- [ ] Deploy/Infrastructure

## Checklist
- [ ] Code follows project style
- [ ] Tests pass locally
- [ ] Docker build succeeds
- [ ] Documentation updated
- [ ] No Phase 1 files modified
```

### Code Review Guidelines

- Review within 24 hours
- Check for:
  - No Phase 1 file modifications
  - Code quality and style
  - Test coverage
  - Documentation updates
- Approve or request changes
- Squash merge to phase-2

## Integration Points

### Shared Files (Coordinate Changes)

These files are shared and require coordination:

| File | Owner | Others Can |
|------|-------|------------|
| `deploy/config.env.example` | Person C | Add service-specific vars |
| `deploy/docker-compose.local.yml` | Person C | Request service additions |
| `docs/api_contracts_phase2.md` | Shared | Edit own service sections |
| `docs/kafka_contracts_phase2.md` | Person B | Add topics as needed |

### Sync Meetings

- Daily standup (15 min): Progress updates, blockers
- Integration sync (2x/week): Merge conflicts, shared files

## Resolving Conflicts

### If You Have Merge Conflicts

```bash
# Update phase-2
git checkout phase-2
git pull origin phase-2

# Go back to your branch and merge
git checkout phase-2/your-feature
git merge phase-2

# Resolve conflicts in your editor
# Then:
git add .
git commit -m "merge: resolve conflicts with phase-2"
git push origin phase-2/your-feature
```

### Prevention Tips

1. Pull from phase-2 daily
2. Keep changes focused on your assigned files
3. Communicate before modifying shared files
4. Small, frequent PRs over large ones

## Release Process

### Merging to Main (End of Phase 2)

1. Ensure all PRs are merged to phase-2
2. Run full test suite
3. Verify Terraform plan is unchanged (no infra drift)
4. Create PR from phase-2 to main
5. Tag release: `phase-2-complete`

```bash
# Final verification
git checkout phase-2
git pull origin phase-2

# Check no Terraform changes
cd terraform
terraform plan  # Should show "No changes"

# Merge to main
git checkout main
git merge phase-2
git tag -a phase-2-complete -m "Phase 2 Microservices Complete"
git push origin main --tags
```

## Quick Reference

### Common Commands

```bash
# Switch to phase-2
git checkout phase-2

# Create feature branch
git checkout -b phase-2/my-feature

# Update from phase-2
git fetch origin
git merge origin/phase-2

# Push feature branch
git push -u origin phase-2/my-feature

# View branches
git branch -a | grep phase-2
```

### Emergency: Undo Last Commit

```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Undo last commit, discard changes (CAREFUL!)
git reset --hard HEAD~1
```

---

**Remember:** Phase 1 infrastructure is complete and stable. All our work is additive - we're building ON TOP of Phase 1, not modifying it.

