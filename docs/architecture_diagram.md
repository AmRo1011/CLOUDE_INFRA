# Architecture Diagrams - Cloud Learning Platform

## Network Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                           AWS Cloud                                  │
│  Region: us-east-1                                                   │
│                                                                       │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃  VPC: 10.0.0.0/16                                              ┃  │
│  ┃                                                                 ┃  │
│  ┃  ┌─────────────────────────────────────────────────────────┐  ┃  │
│  ┃  │  Availability Zone: us-east-1a                          │  ┃  │
│  ┃  │                                                          │  ┃  │
│  ┃  │  ┌──────────────────────────────────────────────────┐  │  ┃  │
│  ┃  │  │  Public Subnet: 10.0.1.0/24                      │  │  ┃  │
│  ┃  │  │                                                   │  │  ┃  │
│  ┃  │  │  ┌────────────────────┐                          │  │  ┃  │
│  ┃  │  │  │   Nginx Gateway    │                          │  │  ┃  │
│  ┃  │  │  │    (t3.micro)      │◄──── Internet           │  │  ┃  │
│  ┃  │  │  │  Public IP: x.x.x.x│                          │  │  ┃  │
│  ┃  │  │  └─────────┬──────────┘                          │  │  ┃  │
│  ┃  │  └────────────┼─────────────────────────────────────┘  │  ┃  │
│  ┃  │               │                                         │  ┃  │
│  ┃  │  ┌────────────▼─────────────────────────────────────┐  │  ┃  │
│  ┃  │  │  Private App Subnet: 10.0.10.0/24                │  │  ┃  │
│  ┃  │  │                                                   │  │  ┃  │
│  ┃  │  │  ┌──────────────────┐   ┌──────────────────┐    │  │  ┃  │
│  ┃  │  │  │   App Node 1     │   │   Kafka Node     │    │  │  ┃  │
│  ┃  │  │  │   (t3.small)     │   │   (t3.small)     │    │  │  ┃  │
│  ┃  │  │  │                  │   │                  │    │  │  ┃  │
│  ┃  │  │  │  ┌────────────┐  │   │  ┌────────────┐ │    │  │  ┃  │
│  ┃  │  │  │  │  Chat Svc  │  │   │  │   Kafka    │ │    │  │  ┃  │
│  ┃  │  │  │  │            │  │   │  │  (Broker)  │ │    │  │  ┃  │
│  ┃  │  │  │  └────────────┘  │   │  └────────────┘ │    │  │  ┃  │
│  ┃  │  │  │  ┌────────────┐  │   │  ┌────────────┐ │    │  │  ┃  │
│  ┃  │  │  │  │  User Mgmt │  │   │  │ Zookeeper  │ │    │  │  ┃  │
│  ┃  │  │  │  │            │  │   │  │            │ │    │  │  ┃  │
│  ┃  │  │  │  └────────────┘  │   │  └────────────┘ │    │  │  ┃  │
│  ┃  │  │  └──────────────────┘   └──────────────────┘    │  │  ┃  │
│  ┃  │  │                                                   │  │  ┃  │
│  ┃  │  │  ┌─────────────────────────────────────┐        │  │  ┃  │
│  ┃  │  │  │  NAT Gateway                        │        │  │  ┃  │
│  ┃  │  │  │  (Provides internet to private)     │        │  │  ┃  │
│  ┃  │  │  └─────────────────────────────────────┘        │  │  ┃  │
│  ┃  │  └───────────────────────────────────────────────────┘  │  ┃  │
│  ┃  │                                                          │  ┃  │
│  ┃  │  ┌───────────────────────────────────────────────────┐  │  ┃  │
│  ┃  │  │  DB Subnet: 10.0.20.0/24                         │  │  ┃  │
│  ┃  │  │                                                   │  │  ┃  │
│  ┃  │  │  ┌─────────────────────────────────────────┐    │  │  ┃  │
│  ┃  │  │  │   RDS PostgreSQL (db.t3.micro)         │    │  │  ┃  │
│  ┃  │  │  │                                         │    │  │  ┃  │
│  ┃  │  │  │   Database: platform_main              │    │  │  ┃  │
│  ┃  │  │  │   Schemas: user_mgmt, chat,            │    │  │  ┃  │
│  ┃  │  │  │            document, quiz              │    │  │  ┃  │
│  ┃  │  │  └─────────────────────────────────────────┘    │  │  ┃  │
│  ┃  │  └───────────────────────────────────────────────────┘  │  ┃  │
│  ┃  └──────────────────────────────────────────────────────────┘  ┃  │
│  ┃                                                                 ┃  │
│  ┃  ┌─────────────────────────────────────────────────────────┐  ┃  │
│  ┃  │  Availability Zone: us-east-1b                          │  ┃  │
│  ┃  │                                                          │  ┃  │
│  ┃  │  ┌──────────────────────────────────────────────────┐  │  ┃  │
│  ┃  │  │  Public Subnet: 10.0.2.0/24                      │  │  ┃  │
│  ┃  │  │  (Reserved for HA expansion)                     │  │  ┃  │
│  ┃  │  └──────────────────────────────────────────────────┘  │  ┃  │
│  ┃  │                                                          │  ┃  │
│  ┃  │  ┌──────────────────────────────────────────────────┐  │  ┃  │
│  ┃  │  │  Private App Subnet: 10.0.11.0/24                │  │  ┃  │
│  ┃  │  │                                                   │  │  ┃  │
│  ┃  │  │  ┌──────────────────┐                            │  │  ┃  │
│  ┃  │  │  │   App Node 2     │                            │  │  ┃  │
│  ┃  │  │  │   (t3.small)     │                            │  │  ┃  │
│  ┃  │  │  │                  │                            │  │  ┃  │
│  ┃  │  │  │  ┌────────────┐  │                            │  │  ┃  │
│  ┃  │  │  │  │  Doc Svc   │  │                            │  │  ┃  │
│  ┃  │  │  │  └────────────┘  │                            │  │  ┃  │
│  ┃  │  │  │  ┌────────────┐  │                            │  │  ┃  │
│  ┃  │  │  │  │  Quiz Svc  │  │                            │  │  ┃  │
│  ┃  │  │  │  └────────────┘  │                            │  │  ┃  │
│  ┃  │  │  └──────────────────┘                            │  │  ┃  │
│  ┃  │  └──────────────────────────────────────────────────┘  │  ┃  │
│  ┃  │                                                          │  ┃  │
│  ┃  │  ┌──────────────────────────────────────────────────┐  │  ┃  │
│  ┃  │  │  DB Subnet: 10.0.21.0/24                         │  │  ┃  │
│  ┃  │  │  (Reserved for Multi-AZ RDS)                     │  │  ┃  │
│  ┃  │  └──────────────────────────────────────────────────┘  │  ┃  │
│  ┃  └──────────────────────────────────────────────────────────┘  ┃  │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  S3 Storage (Regional Service)                              │    │
│  │                                                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │    │
│  │  │  user-mgmt   │  │  document    │  │    quiz      │     │    │
│  │  │   bucket     │  │   bucket     │  │   bucket     │     │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Service Communication Flow

```
┌──────────┐
│  Client  │
│ (Browser)│
└─────┬────┘
      │ HTTP/HTTPS
      ▼
┌─────────────────┐
│ Nginx Gateway   │
│  (Port 80/443)  │
└────┬────┬───┬───┘
     │    │   │
     │    │   └────────────────────────┐
     │    │                            │
     │    └───────────────┐            │
     │                    │            │
     ▼                    ▼            ▼
┌──────────┐      ┌───────────┐  ┌──────────┐
│  Chat    │      │ Document  │  │  Quiz    │
│ Service  │      │  Service  │  │ Service  │
│ (8000)   │      │  (8002)   │  │ (8003)   │
└────┬─────┘      └─────┬─────┘  └────┬─────┘
     │                  │              │
     │ Produce Events   │              │
     └──────┬───────────┴──────────────┘
            ▼
    ┌───────────────┐
    │  Kafka        │
    │  Topics:      │
    │  - chat.msg   │
    │  - doc.upload │
    │  - quiz.gen   │
    └───────┬───────┘
            │ Consume Events
            │
    ┌───────▼───────────────────┐
    │  All Services Subscribe   │
    │  to Relevant Topics       │
    └───────────────────────────┘
```

## Data Flow - Document Upload Example

```
1. User uploads PDF document
         │
         ▼
2. Nginx routes to Document Service
         │
         ▼
3. Document Service:
   ├─► Store PDF in S3 bucket (document-service-storage)
   ├─► Extract text from PDF
   ├─► Store metadata in PostgreSQL (document schema)
   └─► Publish event: "document.uploaded"
         │
         ▼
4. Kafka distributes event
         │
         ├─► Quiz Service consumes event
         │   ├─► Generate quiz from document
         │   ├─► Store quiz in S3 (quiz-service-storage)
         │   ├─► Store quiz metadata in PostgreSQL (quiz schema)
         │   └─► Publish event: "quiz.generated"
         │
         └─► Chat Service consumes event
             └─► Update conversation context with document knowledge
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Layer 1: Network Security                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • VPC Isolation                                 │  │
│  │  • Security Groups (Firewall Rules)             │  │
│  │  │  - nginx-sg: 80, 443 from internet           │  │
│  │  │  - app-sg: 8000-8100 from nginx-sg only      │  │
│  │  │  - kafka-sg: 9092, 2181 from app-sg only     │  │
│  │  │  - db-sg: 5432 from app-sg only              │  │
│  │  • Private Subnets (no direct internet)         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Layer 2: Data Encryption                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • EBS Volumes: Encrypted at rest               │  │
│  │  • RDS Storage: Encrypted at rest (AES-256)     │  │
│  │  • S3 Buckets: Server-side encryption (SSE-S3)  │  │
│  │  • TLS in Transit (between services)            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Layer 3: Access Control                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • SSH Key-based authentication                  │  │
│  │  • Database user separation per service          │  │
│  │  • S3 bucket policies (per-service access)       │  │
│  │  • Schema-level database isolation               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Layer 4: Application Security (RBAC)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • JWT-based authentication                      │  │
│  │  • Role-based access control                     │  │
│  │  │  - Admin: Full access                         │  │
│  │  │  - Instructor: Create/grade quizzes           │  │
│  │  │  - Student: Use services, take quizzes        │  │
│  │  • Permission checks per API endpoint            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Scaling Path (Dev → Production)

```
Development (Current)           Production (Phase 3+)
─────────────────────          ──────────────────────

Nginx (1x t3.micro)      →     ALB + Auto Scaling (2-10 instances)
App Nodes (2x t3.small)  →     ECS/EKS Cluster (5-20 containers)
Kafka (1x broker)        →     Kafka Cluster (3+ brokers + 3 ZK)
RDS (1x db.t3.micro)     →     RDS Multi-AZ + Read Replicas
NAT GW (1x)              →     NAT GW per AZ (2+)
Single Schema            →     Separate RDS per service

Cost: ~$50-100/month           Cost: ~$1,500-3,000/month
```

---

## Future Architecture (Phase 2-3)

```
┌────────────────────────────────────────────────────────────┐
│                 Enhanced Architecture                       │
│                                                            │
│  ┌──────────────┐                                         │
│  │     ALB      │  (Application Load Balancer)            │
│  │  + WAF +     │                                         │
│  │  Shield      │                                         │
│  └──────┬───────┘                                         │
│         │                                                 │
│         ▼                                                 │
│  ┌────────────────────────────┐                          │
│  │   ECS/Fargate Cluster      │                          │
│  │   (Auto-scaling)           │                          │
│  │                            │                          │
│  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ │                          │
│  │  │Svc│ │Svc│ │Svc│ │Svc│ │                          │
│  │  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │                          │
│  │  └───┘ └───┘ └───┘ └───┘ │                          │
│  └────────────┬───────────────┘                          │
│               │                                           │
│  ┌────────────▼────────────────┐                         │
│  │   MSK (Managed Kafka)       │                         │
│  │   - Multi-AZ                │                         │
│  │   - Auto-scaling            │                         │
│  └─────────────────────────────┘                         │
│                                                           │
│  ┌─────────────────────────────┐                         │
│  │   RDS Multi-AZ + Replicas   │                         │
│  │   - Primary + Read Replicas │                         │
│  │   - Automated backups       │                         │
│  └─────────────────────────────┘                         │
│                                                           │
│  ┌─────────────────────────────┐                         │
│  │   CloudWatch + X-Ray        │                         │
│  │   - Distributed tracing     │                         │
│  │   - Metrics & Alarms        │                         │
│  └─────────────────────────────┘                         │
│                                                           │
└────────────────────────────────────────────────────────────┘
```

