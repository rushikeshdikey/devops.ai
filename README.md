# DevOps Automation UI

A comprehensive full-stack application for managing, validating, and versioning Infrastructure as Code (IaC) configurations with policy enforcement and audit logging.

## Features

### Backend (FastAPI + Python)
- **Authentication**: JWT-based auth with access/refresh tokens
- **RBAC**: Role-based access control (ADMIN, MAINTAINER, VIEWER)
- **Projects & Configurations**: Organize IaC assets by project
- **Version Control**: Automatic versioning with checksum tracking
- **Validation**: Built-in validators for:
  - Kubernetes YAML (apiVersion, kind, resource limits, image tags, replicas)
  - Terraform (provider blocks, resource tags, variable usage)
  - Generic YAML (structure, size limits, naming conventions)
- **Dry Run**: Mock execution planning for configs
- **Policy Engine**: Custom policy language for config validation
- **Audit Logging**: Comprehensive activity tracking
- **Database**: PostgreSQL with async SQLAlchemy 2.0 + Alembic migrations

### Frontend (React 18 + TypeScript + Vite)
- **Modern Stack**: React 18, TypeScript, Vite, TailwindCSS
- **UI Components**: Custom shadcn/ui-inspired components
- **State Management**: Zustand for global state, TanStack Query for server state
- **Code Editor**: Monaco Editor integration for YAML/HCL editing
- **Real-time Validation**: Live validation feedback in the editor
- **Version Diff**: Side-by-side version comparison
- **Responsive Design**: Mobile-friendly interface

## Architecture

```
/devops-automation-ui
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routers/           # API endpoints
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── validators/   # Config validators
│   │   │   └── policy/       # Policy engine
│   │   ├── main.py           # FastAPI app
│   │   └── seed.py           # Database seeding
│   └── web/                   # React frontend
│       ├── src/
│       │   ├── components/   # UI components
│       │   ├── pages/        # Page components
│       │   ├── services/     # API client
│       │   ├── store/        # State management
│       │   └── lib/          # Utilities
│       └── package.json
├── alembic/                   # Database migrations
├── docker/                    # Dockerfiles
├── docker-compose.yml         # Service orchestration
├── Makefile                   # Common commands
└── README.md
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Make (optional, for convenience)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd devops.ai
```

2. **Start the services**
```bash
make dev
# or
docker-compose up -d db
docker-compose run --rm api alembic upgrade head
docker-compose run --rm api python apps/api/seed.py
docker-compose up api
```

3. **Access the application**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Demo Credentials

The seed script creates the following demo users:

| Email | Password | Role |
|-------|----------|------|
| admin@demo.io | changeme | ADMIN |
| maint@demo.io | changeme | MAINTAINER |
| viewer@demo.io | changeme | VIEWER |

## Available Commands

### Makefile Commands
```bash
make dev      # Start development environment
make migrate  # Run database migrations
make seed     # Seed database with demo data
make build    # Build Docker images
make up       # Start all services
make down     # Stop all services
make logs     # View logs
make clean    # Clean up containers and volumes
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token

### Users
- `GET /api/users/me` - Get current user
- `GET /api/users` - List all users (ADMIN)
- `PATCH /api/users/{id}` - Update user role (ADMIN)

### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{id}` - Get project
- `PATCH /api/projects/{id}` - Update project

### Configurations
- `POST /api/projects/{id}/configs` - Create config
- `GET /api/projects/{id}/configs` - List configs
- `GET /api/configs/{id}` - Get config
- `DELETE /api/configs/{id}` - Delete config

### Versions
- `POST /api/configs/{id}/versions` - Create version
- `GET /api/configs/{id}/versions` - List versions
- `GET /api/versions/{id}` - Get version
- `GET /api/versions/{id}/diff?base=prev` - Get diff

### Validation
- `POST /api/versions/{id}/validate` - Validate version
- `POST /api/versions/{id}/dry-run` - Mock dry-run

### Policies
- `POST /api/policies` - Create policy
- `GET /api/policies` - List policies
- `DELETE /api/policies/{id}` - Delete policy
- `POST /api/policy/validate` - Test policy rule

### Audit
- `GET /api/audit` - List audit logs

### Health
- `GET /api/health` - Health check
- `GET /api/metrics` - Metrics

## Configuration

### Environment Variables

**Backend (apps/api/.env)**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/devops
JWT_SECRET=your-secret-key-min-32-characters
ACCESS_TOKEN_TTL_MIN=15
REFRESH_TOKEN_TTL_DAYS=7
CORS_ORIGIN=http://localhost:5173
LOG_LEVEL=info
```

**Frontend (apps/web/.env)**
```env
VITE_API_URL=http://localhost:8000
```

## Validation Rules

### Kubernetes YAML
- ✅ Valid `apiVersion`, `kind`, `metadata.name`
- ✅ Container resource requests/limits defined
- ❌ No `:latest` image tags
- ⚠️  Warning if replicas < 2 for Deployments

### Terraform
- ✅ Provider block present
- ✅ Required tags: `environment`, `owner`
- ⚠️  Unused variables detected

### Generic YAML
- ✅ Valid YAML syntax
- ✅ Root must be a mapping
- ✅ File size < 1MB
- ⚠️  Non-snake_case keys

## Policy Engine

Custom policy language supporting:

```
INCLUDES('text')              # Check if content contains text
MATCHES('regex')              # Check if content matches regex
NOT expression                # Negate
expression AND expression     # Logical AND
expression OR expression      # Logical OR
```

**Example Policy**
```
INCLUDES('owner:') AND NOT MATCHES(':\s*latest\b')
```

This policy ensures configs have an `owner` tag and don't use `:latest` image tags.

## Security Features

- JWT authentication with refresh tokens
- Password hashing with bcrypt (12 rounds)
- RBAC (Role-Based Access Control)
- CORS protection
- SQL injection prevention (parameterized queries)
- Request validation with Pydantic

## Database Schema

**Tables**
- `users` - User accounts with roles
- `projects` - Project containers
- `configs` - Configuration definitions
- `config_versions` - Versioned config content
- `validation_runs` - Validation results
- `policies` - Policy rules
- `audit_logs` - Activity tracking

## Development

### Project Structure
- **Monorepo** with separate backend and frontend
- **TypeScript** for type safety
- **Async/Await** throughout the stack
- **RESTful API** design
- **Component-based** frontend architecture

## Deployment

### Production Build

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose run --rm api alembic upgrade head
```

### Environment-Specific Configuration
- Use `.env` files for configuration
- Change `JWT_SECRET` in production
- Use managed PostgreSQL in production
- Configure CORS for production domain

## License

This project is licensed under the MIT License.

---

Built with ❤️ using FastAPI, React, and TypeScript