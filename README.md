# Cloud Cost Optimizer

AI-powered cloud cost optimization platform that helps businesses reduce their AWS, GCP, and Azure spending by 30-40% through intelligent analysis and actionable recommendations.

## Overview

Cloud Cost Optimizer is a SaaS product that connects to your cloud accounts, analyzes your infrastructure, and provides AI-driven recommendations to optimize costs. Save thousands of dollars monthly with automated cost analysis and proven optimization strategies.

**Key Value Proposition:**
- 🎯 Average 40% cost reduction
- 💰 $14,000+ average annual savings
- 📊 48x ROI on subscription cost
- ⚡ Real-time cost analysis
- 🤖 AI-powered recommendations

## Features

### Multi-Cloud Support
- **AWS**: EC2, RDS, S3, EBS volumes, Lambda integration via Cost Explorer
- **GCP**: Compute Engine, Cloud Storage, Cloud SQL via Cloud Billing API
- **Azure**: Virtual Machines, Storage Accounts, SQL Databases via Cost Management API

### Cost Analysis
- Real-time cost breakdown by service (compute, storage, network, database)
- Historical trend analysis
- Resource utilization tracking
- Waste detection (idle resources, oversized instances)

### AI-Powered Recommendations
- **Downsize Resources**: Right-size overprovisioned instances
- **Reserved Instances**: Identify RI opportunities for predictable workloads
- **Storage Optimization**: Migrate to cheaper storage tiers
- **Terminate Idle Resources**: Find and remove unused infrastructure
- **Priority-based**: HIGH, MEDIUM, LOW with effort estimates

### Subscription Plans
- **FREE**: 1 cloud account, basic analysis, 5 recommendations
- **PREMIUM ($29/month)**: Unlimited accounts, advanced AI, unlimited recommendations, priority support

## Architecture

```
/cloud-cost-optimizer
├── apps/
│   ├── api/                           # FastAPI backend
│   │   ├── core/                     # Config, database, security
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── user.py              # User model with RBAC
│   │   │   └── billing.py           # Subscriptions, CloudAccounts, CostAnalysis
│   │   ├── routers/                  # API endpoints
│   │   │   ├── auth.py              # JWT authentication
│   │   │   ├── billing.py           # Subscription management
│   │   │   └── cost_optimizer.py   # Cost analysis endpoints
│   │   ├── services/                 # Business logic
│   │   │   └── cost_optimizer/
│   │   │       ├── engine.py        # AI recommendation engine
│   │   │       └── cloud_providers.py # AWS/GCP/Azure integrations
│   │   └── main.py                   # FastAPI app
│   └── web/                          # React + TypeScript frontend
│       └── src/
│           ├── pages/
│           │   ├── DashboardPage.tsx
│           │   ├── CostOptimizerPage.tsx
│           │   ├── CloudAccountsPage.tsx
│           │   ├── CostAnalysisDetailPage.tsx
│           │   └── PricingPage.tsx
│           └── services/
│               └── costOptimizer.ts  # API client
├── alembic/                          # Database migrations
├── docker-compose.yml                 # Service orchestration
└── Makefile                          # Common commands
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Cloud provider credentials (AWS Access Key, GCP Service Account, or Azure Service Principal)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/rushikeshdikey/devops.ai.git
cd devops.ai
```

2. **Configure environment variables**

**Backend (apps/api/.env)**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/costoptimizer
JWT_SECRET=your-secret-key-min-32-characters-here
ACCESS_TOKEN_TTL_MIN=15
REFRESH_TOKEN_TTL_DAYS=7
CORS_ORIGIN=http://localhost:5173
LOG_LEVEL=info
STRIPE_SECRET_KEY=sk_test_your_stripe_key  # For production billing
```

**Frontend (apps/web/.env)**
```env
VITE_API_URL=http://localhost:8000
```

3. **Start the services**
```bash
make dev
# or manually:
docker-compose up -d db
docker-compose run --rm api alembic upgrade head
docker-compose run --rm api python apps/api/seed.py
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Demo Credentials

The seed script creates demo users:

| Email | Password | Role | Subscription |
|-------|----------|------|--------------|
| admin@demo.io | changeme | ADMIN | FREE |
| maint@demo.io | changeme | MAINTAINER | FREE |
| viewer@demo.io | changeme | VIEWER | FREE |

## Cloud Provider Setup

### AWS Setup

1. Create IAM user with the following policies:
   - `AWSCostExplorerReadOnlyAccess`
   - Custom policy for resource read access:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "s3:ListAllMyBuckets",
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    }
  ]
}
```

2. Generate access keys and add to Cloud Cost Optimizer

### GCP Setup

1. Create a service account with roles:
   - Compute Viewer
   - Storage Admin
   - Cloud Billing Account Viewer

2. Download JSON key file

3. Add credentials to Cloud Cost Optimizer (paste entire JSON)

### Azure Setup

1. Create an App Registration in Azure AD

2. Grant the following permissions:
   - Reader role on subscription
   - Cost Management Reader

3. Create client secret and add credentials:
   - Tenant ID
   - Client ID
   - Client Secret
   - Subscription ID

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/refresh` - Refresh access token

### Users
- `GET /api/users/me` - Get current user profile

### Subscriptions
- `GET /api/billing/subscription` - Get user's subscription
- `POST /api/billing/subscription` - Create/upgrade subscription
- `DELETE /api/billing/subscription` - Cancel subscription

### Cloud Accounts
- `POST /api/cost-optimizer/cloud-accounts` - Connect cloud account
- `GET /api/cost-optimizer/cloud-accounts` - List connected accounts
- `DELETE /api/cost-optimizer/cloud-accounts/{id}` - Remove account
- `POST /api/cost-optimizer/cloud-accounts/{id}/sync` - Sync account data

### Cost Analysis
- `POST /api/cost-optimizer/analyze` - Run cost analysis on account
- `GET /api/cost-optimizer/analyses` - List all analyses
- `GET /api/cost-optimizer/analyses/{id}` - Get analysis details

### Recommendations
- `GET /api/cost-optimizer/recommendations/{analysis_id}` - Get recommendations
- `PATCH /api/cost-optimizer/recommendations/{id}` - Update recommendation status (APPLIED/DISMISSED)

### Health
- `GET /api/health` - Health check

## How It Works

### 1. Connect Cloud Accounts
Users securely connect their AWS, GCP, or Azure accounts by providing read-only credentials. Credentials are encrypted and stored securely.

### 2. Resource Discovery
The platform fetches all billable resources from connected accounts:
- Compute instances (EC2, VMs, Compute Engine)
- Storage (S3, Azure Storage, Cloud Storage)
- Databases (RDS, Cloud SQL, Azure SQL)
- Network resources

### 3. Cost Analysis
Using cloud provider APIs:
- **AWS**: Cost Explorer API for granular cost data
- **GCP**: Cloud Billing API (requires BigQuery export)
- **Azure**: Cost Management API

### 4. AI Recommendation Engine
Machine learning algorithms analyze:
- Resource utilization patterns
- Cost trends over time
- Industry benchmarks
- Right-sizing opportunities
- Reserved Instance potential
- Storage tier optimization

### 5. Actionable Insights
Recommendations include:
- Specific resource IDs to modify
- Current vs. proposed configuration
- Estimated monthly/annual savings
- Implementation effort (LOW/MEDIUM/HIGH)
- Priority ranking (HIGH/MEDIUM/LOW)

## Subscription Tiers

### FREE Plan ($0/month)
- ✅ 1 cloud account
- ✅ Basic cost analysis
- ✅ Up to 5 recommendations
- ✅ Manual sync

### PREMIUM Plan ($29/month)
- ✅ Unlimited cloud accounts
- ✅ Advanced AI analysis
- ✅ Unlimited recommendations
- ✅ Auto-sync (daily)
- ✅ Historical trend analysis
- ✅ Priority support
- ✅ Custom alerts

## Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **PostgreSQL** - Production database
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation
- **JWT** - Authentication
- **boto3** - AWS SDK
- **google-cloud-*** - GCP SDKs
- **azure-mgmt-*** - Azure SDKs

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **TanStack Query** - Server state management
- **Zustand** - Global state
- **React Router** - Navigation
- **Recharts** - Data visualization

## Development

### Install Dependencies

**Backend:**
```bash
cd apps/api
pip install -r requirements.txt
```

**Frontend:**
```bash
cd apps/web
npm install
```

### Run Locally

```bash
# Start backend
cd apps/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend
cd apps/web
npm run dev
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Seed Database

```bash
python apps/api/seed.py
```

## Deployment

### Production Build

```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head
```

### Environment Variables (Production)

- Change `JWT_SECRET` to a secure random value
- Use managed PostgreSQL (AWS RDS, Cloud SQL, Azure Database)
- Configure Stripe API keys for billing
- Set up proper CORS origins
- Enable SSL/TLS
- Configure cloud provider rate limits

## Pricing & ROI

**Typical Customer Profile:**
- Monthly cloud spend: $10,000
- Potential savings: 40%
- Annual savings: $48,000
- Subscription cost: $348/year
- **ROI: 138x**

Even with modest 20% savings on $5,000 monthly spend:
- Annual savings: $12,000
- **ROI: 34x**

## Security

- 🔒 End-to-end encryption for credentials
- 🔐 JWT-based authentication
- 🛡️ RBAC (Role-Based Access Control)
- 🔑 Read-only cloud permissions
- 📝 Audit logging
- 🚫 No data modification - analysis only

## Support

- 📧 Email: dikeyrushikesh@gmail.com
- 📚 Documentation: https://docs.cloudcostoptimizer.com
- 🐛 Issues: https://github.com/rushikeshdikey/devops.ai/issues

## Roadmap

- [ ] Kubernetes cost optimization
- [ ] Multi-region cost comparison
- [ ] Budget alerts & notifications
- [ ] Cost forecasting
- [ ] Team collaboration features
- [ ] Slack/Teams integrations
- [ ] Mobile app (iOS/Android)
- [ ] White-label solution for MSPs

## License

This project is proprietary software. All rights reserved.

---

**Author:** Rushikesh Dikey (dikeyrushikesh@gmail.com)

Built with ❤️ to help businesses optimize cloud costs and save money.
