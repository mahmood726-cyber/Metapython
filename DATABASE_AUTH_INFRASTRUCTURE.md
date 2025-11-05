# MetaPython Database & Authentication Infrastructure

## 🚀 Overview

This document describes the comprehensive database persistence and authentication infrastructure added to MetaPython 0.8.0.

## 📊 Architecture

```
MetaPython Infrastructure
├── Database Layer (PostgreSQL/SQLite/MySQL)
│   ├── SQLAlchemy ORM Models
│   ├── Connection Management
│   ├── CRUD Operations
│   └── Alembic Migrations
├── Authentication System
│   ├── JWT Token-based Auth
│   ├── OAuth2 Password Flow
│   ├── Role-based Authorization
│   └── Permission Management
├── CLI Tool
│   ├── Database Commands
│   ├── User Management
│   ├── Project Operations
│   └── Server Control
└── Docker Deployment
    ├── Multi-container Setup
    ├── PostgreSQL + Redis
    ├── API + Frontend
    └── Grafana + Prometheus
```

## 🗄️ Database Layer

### Models

**User Model** (`metapython/database/models.py:User`)
- Username, email, password (bcrypt hashed)
- Full name, institution, ORCID
- Role-based access (Admin, Researcher, Reviewer, Viewer)
- Email verification and account status
- Audit timestamps (created, updated, last login)

**MetaAnalysisProject Model**
- Project metadata (title, description, research question)
- PICOS criteria (Population, Intervention, Comparator, Outcome, Study design)
- Effect measure configuration (SMD, MD, OR, RR, HR, Proportion, Correlation)
- Status tracking (Draft, In Progress, Completed, Published, Archived)
- Public/private visibility

**Study Model**
- Study identification (study_id, title, authors, year, journal, DOI, PMID)
- Effect size data (effect, SE, variance, confidence intervals)
- Sample sizes (intervention, control, total)
- Screening status (Pending, Included, Excluded, Uncertain)
- Risk of bias assessment (7 Cochrane RoB 2 domains)
- Flexible moderators (JSON storage)

**Analysis Model**
- Versioning system (multiple analyses per project)
- Analysis configuration (method, tau² estimator)
- Pooled effect estimates with confidence intervals
- Heterogeneity statistics (I², τ², H², Q)
- Prediction intervals
- Publication bias tests (Egger, Begg)
- ML predictions (heterogeneity, bias probability)
- Full results (JSON storage for complex structures)

**AuditLog Model**
- Comprehensive audit trail
- User actions tracking
- Entity changes (old/new values)
- IP address and user agent logging
- Timestamp-based queries

**ProjectCollaborator Model**
- Multi-user collaboration
- Granular permissions (edit, delete, publish)
- User-project many-to-many relationship

### Database Configuration

**Supported Databases:**
- PostgreSQL (production recommended)
- SQLite (development/testing)
- MySQL (optional)

**Environment Variables:**
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/database

# Or components
DB_TYPE=postgresql
DB_USER=metapython
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=metapython
```

**Features:**
- Connection pooling (configurable pool size, timeout, recycle)
- SQLite WAL mode for concurrency
- PostgreSQL connection pre-ping
- Automatic type conversion
- Transaction management

### CRUD Operations

**User CRUD** (`metapython/database/crud.py:UserCRUD`)
```python
# Create user
user = UserCRUD.create_user(
    session,
    username="researcher",
    email="researcher@example.com",
    password="secure_password"
)

# Authenticate
user = UserCRUD.authenticate_user(session, "researcher", "password")

# List users
users = UserCRUD.list_users(session, role=UserRole.RESEARCHER)
```

**Project CRUD** (`ProjectCRUD`)
```python
# Create project
project = ProjectCRUD.create_project(
    session,
    owner_id=user.id,
    title="My Meta-Analysis",
    effect_measure=EffectMeasure.SMD
)

# List user projects
projects = ProjectCRUD.list_user_projects(session, user.id)

# Update project
ProjectCRUD.update_project(session, project_id, user_id, status=AnalysisStatus.COMPLETED)
```

**Study CRUD** (`StudyCRUD`)
```python
# Create study
study = StudyCRUD.create_study(
    session,
    project_id=1,
    study_id="Smith2020",
    title="Study title",
    effect_size=0.5,
    standard_error=0.1
)

# Bulk import
StudyCRUD.bulk_import_studies(session, project_id, studies_data)

# Get included studies
studies = StudyCRUD.get_included_studies(session, project_id)
```

**Analysis CRUD** (`AnalysisCRUD`)
```python
# Create analysis (auto-versioning)
analysis = AnalysisCRUD.create_analysis(
    session,
    project_id=1,
    method="random",
    pooled_effect=0.45,
    pooled_se=0.08,
    ci_lower=0.29,
    ci_upper=0.61,
    p_value=0.001,
    n_studies=25
)

# Get current analysis
current = AnalysisCRUD.get_current_analysis(session, project_id)
```

### Migrations (Alembic)

**Setup:**
```bash
# Initialize database
metapython db init

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Files:**
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Migration environment
- `alembic/versions/001_initial_schema.py` - Initial schema migration

## 🔐 Authentication System

### JWT Token-Based Authentication

**JWTHandler** (`metapython/auth/jwt_handler.py`)

**Token Types:**
1. **Access Token** (30 minutes default)
   - User authentication
   - API endpoint access
   - Contains user_id, username, role

2. **Refresh Token** (7 days default)
   - Long-lived token
   - Generate new access tokens
   - Refresh token rotation

3. **Verification Token** (24 hours)
   - Email verification
   - One-time use

4. **Password Reset Token** (1 hour)
   - Password reset flow
   - One-time use

**Configuration:**
```python
from metapython.auth import JWTConfig, JWTHandler

config = JWTConfig(
    secret_key="your-secret-key",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)

jwt_handler = JWTHandler(config)
```

**Usage:**
```python
# Create access token
access_token = jwt_handler.create_access_token(
    user_id=1,
    username="alice",
    role="researcher"
)

# Verify token
payload = jwt_handler.verify_access_token(access_token)

# Refresh access token
new_access_token = jwt_handler.refresh_access_token(refresh_token)
```

### FastAPI Authentication

**Dependencies** (`metapython/auth/dependencies.py`)

```python
from fastapi import Depends
from metapython.auth import get_current_user, require_admin

@app.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.username}"}

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    # Admin only
    ...
```

**Available Dependencies:**
- `get_current_user` - Get authenticated user
- `get_current_active_user` - Get active user
- `get_current_verified_user` - Get verified user
- `require_role(UserRole.ADMIN)` - Require specific role
- `require_admin` - Admin only
- `require_researcher` - Researcher or higher
- `PermissionChecker(can_edit=True)` - Permission-based

### Authentication Routes

**Endpoints** (`/api/v1/auth`):

```bash
# Register new user
POST /auth/register
{
  "username": "researcher",
  "email": "researcher@example.com",
  "password": "secure_password",
  "full_name": "Dr. Researcher"
}

# Login
POST /auth/login
Form data: username, password
Returns: access_token, refresh_token

# Refresh token
POST /auth/refresh
{
  "refresh_token": "..."
}

# Get current user
GET /auth/me

# Update profile
PUT /auth/me
{
  "full_name": "Updated Name",
  "institution": "University"
}

# Verify email
POST /auth/verify-email/{token}

# Request password reset
POST /auth/password-reset
{
  "email": "user@example.com"
}

# Confirm password reset
POST /auth/password-reset/confirm
{
  "token": "...",
  "new_password": "new_secure_password"
}
```

### Role-Based Authorization

**Role Hierarchy:**
1. **Viewer** (0) - Read-only access
2. **Reviewer** (1) - Can review and comment
3. **Researcher** (2) - Can create and edit projects
4. **Admin** (3) - Full system access

**Permissions:**
- **View**: All roles
- **Edit**: Reviewer, Researcher, Admin
- **Delete**: Researcher, Admin
- **Publish**: Researcher, Admin
- **Admin actions**: Admin only

## 🖥️ CLI Tool

### Installation

```bash
pip install -e .
metapython --help
```

### Commands

**Database Management:**
```bash
# Initialize database
metapython db init

# Reset database
metapython db reset

# Run migrations
metapython db migrate

# Create migration
metapython db makemigration -m "Add column"

# Database status
metapython db status
```

**User Management:**
```bash
# Create user (interactive)
metapython user create

# Create user (command-line)
metapython user create \
  --username alice \
  --email alice@example.com \
  --password secure_pass \
  --role researcher

# List users
metapython user list
metapython user list --role admin
```

**Project Management:**
```bash
# Create project
metapython project create \
  --user-id 1 \
  --title "My Meta-Analysis" \
  --effect-measure smd

# List projects
metapython project list --user-id 1
metapython project list --user-id 1 --status completed
```

**Server Control:**
```bash
# Start API server
metapython server start
metapython server start --port 8000 --reload

# Start frontend
metapython server frontend --port 3000
```

**Analysis:**
```bash
# Run meta-analysis
metapython analyze run \
  --project-id 1 \
  --method random \
  --output results.json
```

## 🐳 Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services

**PostgreSQL** (port 5432)
- Persistent volume for data
- Health checks enabled

**Redis** (port 6379)
- Caching layer
- Persistent AOF

**API** (port 8000)
- FastAPI application
- Auto-migration on startup
- Health check endpoint

**Frontend** (port 3000)
- React application
- Connected to API

**Grafana** (port 3001)
- Monitoring dashboards
- Default credentials: admin/admin

**Prometheus** (port 9090)
- Metrics collection

**Nginx** (ports 80, 443)
- Reverse proxy
- SSL/TLS termination

### Environment Variables

Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql://metapython:secure_password@postgres:5432/metapython

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-very-secure-secret-key-change-this

# Environment
ENVIRONMENT=production
```

### Production Deployment

1. **Update docker-compose.yml:**
   - Change default passwords
   - Set secure JWT_SECRET_KEY
   - Configure SSL certificates

2. **Deploy:**
```bash
docker-compose -f docker-compose.yml up -d
```

3. **Initialize database:**
```bash
docker-compose exec api metapython db init
```

4. **Create admin user:**
```bash
docker-compose exec api metapython user create \
  --username admin \
  --email admin@example.com \
  --role admin
```

## 📈 Usage Examples

### Complete Workflow

```python
from metapython.database import init_database, get_database
from metapython.database import UserCRUD, ProjectCRUD, StudyCRUD, AnalysisCRUD
from metapython.auth import get_jwt_handler

# 1. Initialize database
db = init_database("postgresql://localhost/metapython")

# 2. Create user
with db.session_scope() as session:
    user = UserCRUD.create_user(
        session,
        username="researcher",
        email="researcher@example.com",
        password="secure_password"
    )

# 3. Generate auth token
jwt_handler = get_jwt_handler()
access_token = jwt_handler.create_access_token(
    user_id=user.id,
    username=user.username
)

# 4. Create project
with db.session_scope() as session:
    project = ProjectCRUD.create_project(
        session,
        owner_id=user.id,
        title="Efficacy of Intervention X",
        description="Systematic review and meta-analysis",
        effect_measure=EffectMeasure.SMD
    )

# 5. Add studies
with db.session_scope() as session:
    study = StudyCRUD.create_study(
        session,
        project_id=project.id,
        study_id="Smith2020",
        title="Study title",
        authors="Smith J, Doe A",
        year=2020,
        effect_size=0.5,
        standard_error=0.1,
        variance=0.01,
        status=StudyStatus.INCLUDED
    )

# 6. Run analysis
from metapython.core.meta_analysis import run_meta_analysis

with db.session_scope() as session:
    studies = StudyCRUD.get_included_studies(session, project.id)
    effects = [s.effect_size for s in studies]
    variances = [s.variance for s in studies]

    result = run_meta_analysis(effects, variances, method="random")

    # Save analysis
    analysis = AnalysisCRUD.create_analysis(
        session,
        project_id=project.id,
        method="random",
        pooled_effect=result['pooled_effect'],
        pooled_se=result['pooled_se'],
        ci_lower=result['ci_lower'],
        ci_upper=result['ci_upper'],
        p_value=result['p_value'],
        i2=result.get('i2'),
        tau2=result.get('tau2'),
        n_studies=len(studies)
    )
```

## 🔒 Security Best Practices

1. **JWT Secret Key:**
   - Use cryptographically secure random key
   - Never commit to version control
   - Rotate periodically

2. **Database:**
   - Use strong passwords
   - Enable SSL/TLS connections
   - Regular backups
   - Limited user permissions

3. **API:**
   - Rate limiting (not yet implemented)
   - CORS configuration
   - HTTPS only in production
   - Input validation (Pydantic)

4. **Passwords:**
   - Bcrypt hashing
   - Minimum 8 characters
   - No password in logs or responses

## 📊 Database Schema Diagram

```sql
users
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── hashed_password
├── role (ENUM)
└── ...

projects
├── id (PK)
├── owner_id (FK → users.id)
├── title
├── effect_measure (ENUM)
├── status (ENUM)
└── ...

studies
├── id (PK)
├── project_id (FK → projects.id)
├── study_id
├── effect_size
├── standard_error
├── status (ENUM)
└── ...

analyses
├── id (PK)
├── project_id (FK → projects.id)
├── version
├── is_current
├── pooled_effect
├── heterogeneity stats
└── ...

audit_logs
├── id (PK)
├── user_id (FK → users.id)
├── action
├── entity_type/id
└── ...

project_collaborators
├── id (PK)
├── project_id (FK → projects.id)
├── user_id (FK → users.id)
├── permissions
└── ...
```

## 🚀 What's Next (v0.9.0)

Planned features:
1. **Redis caching layer** - API response caching
2. **Real-time WebSocket** - Collaboration features
3. **Email service** - Verification and notifications
4. **API rate limiting** - DDoS protection
5. **Advanced permissions** - Fine-grained access control
6. **Audit log API** - Query compliance logs
7. **Data export** - CSV, Excel, SPSS formats
8. **Backup/restore** - Database backup utilities

---

**MetaPython 0.8.0** - Production-Ready Database & Authentication Infrastructure! 🎉
