# Environment Configuration Guide

This guide explains how to configure environment variables and secrets for Plant Assistant across different environments.

## 🔐 Security First

**NEVER commit secrets to version control!** All sensitive information should be stored in:
- Environment variables (local development)
- GitHub Secrets (CI/CD)
- Secure configuration management (production)

## 📋 Required Environment Variables

### Backend Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `SECRET_KEY` | JWT secret key | ✅ Yes | - | `your-super-secret-key-here` |
| `DATABASE_URL` | PostgreSQL connection string | ✅ Yes | - | `postgresql+asyncpg://user:pass@host:5432/db` |
| `ENVIRONMENT` | Application environment | ✅ Yes | `development` | `development`, `staging`, `production` |

### Database Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `DATABASE_URL` | Main database URL | ✅ Yes | - | `postgresql+asyncpg://postgres:password@localhost:5432/plantdb` |
| `TEST_DATABASE_URL` | Test database URL | 🧪 Testing | Same as DATABASE_URL | `postgresql+asyncpg://postgres:password@localhost:5432/plantdb_test` |

### Email Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `MAIL_SERVER` | SMTP server hostname | 📧 Email | `localhost` | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP server port | 📧 Email | `587` | `587`, `465`, `25` |
| `MAIL_USERNAME` | SMTP username | 📧 Email | - | `your-email@gmail.com` |
| `MAIL_PASSWORD` | SMTP password | 📧 Email | - | `your-app-password` |
| `MAIL_USE_TLS` | Use TLS encryption | 📧 Email | `true` | `true`, `false` |
| `MAIL_FROM` | Default from address | 📧 Email | - | `noreply@yourapp.com` |

### Security & CORS Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `CORS_ORIGINS` | Allowed CORS origins | 🌐 Web | `["http://localhost:3000"]` | `["https://yourapp.com", "https://api.yourapp.com"]` |
| `API_PREFIX` | API route prefix | ⚙️ Optional | `/api/v1` | `/api/v1`, `/v1` |
| `DEBUG` | Enable debug mode | 🐛 Debug | `false` | `true`, `false` |

### Frontend Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | ✅ Yes | `http://localhost:8000` | `https://api.yourapp.com` |
| `NEXT_PUBLIC_APP_NAME` | Application name | ⚙️ Optional | `Plant Assistant` | `My Plant App` |
| `NEXTAUTH_SECRET` | NextAuth secret | 🔐 Auth | - | `your-nextauth-secret` |
| `NEXTAUTH_URL` | Application URL | 🔐 Auth | `http://localhost:3000` | `https://yourapp.com` |

## 🛠️ Environment Setup

### 1. Local Development

Create a `.env` file in the root directory:

```bash
# Copy from .env.example and fill in your values
cp .env.example .env
```

Example `.env` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/plantassistant
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/plantassistant_test

# Security
SECRET_KEY=your-super-secret-development-key-change-in-production
ENVIRONMENT=development

# CORS (for local frontend)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Email (optional for development)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-nextauth-secret-for-development
NEXTAUTH_URL=http://localhost:3000
```

### 2. GitHub Actions / CI

Set these secrets in your GitHub repository settings (`Settings` → `Secrets and variables` → `Actions`):

#### Repository Secrets

```bash
# Core application secrets
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/testdb
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/testdb

# Database credentials
POSTGRES_PASSWORD=your-secure-database-password

# Email configuration
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-email-password

# Application settings
CORS_ORIGINS=["https://your-production-domain.com"]
ENVIRONMENT=production
API_PREFIX=/api/v1

# Frontend settings
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXTAUTH_SECRET=your-nextauth-production-secret
NEXTAUTH_URL=https://your-production-domain.com
```

#### Setting GitHub Secrets

1. Go to your repository on GitHub
2. Click `Settings` → `Secrets and variables` → `Actions`
3. Click `New repository secret`
4. Add each secret with the name and value

### 3. Production Deployment

#### Docker Compose

Update your `docker-compose.yml` or `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - ENVIRONMENT=production
      - CORS_ORIGINS=${CORS_ORIGINS}
      - MAIL_SERVER=${MAIL_SERVER}
      - MAIL_PORT=${MAIL_PORT}
      - MAIL_USERNAME=${MAIL_USERNAME}
      - MAIL_PASSWORD=${MAIL_PASSWORD}
    env_file:
      - .env.prod

  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=${NEXTAUTH_URL}
    env_file:
      - .env.prod
```

## 🔧 Environment-Specific Configuration

### Development
```bash
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/plantassistant_dev
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
MAIL_SERVER=localhost
MAIL_PORT=1025
```

### Testing
```bash
ENVIRONMENT=testing
DEBUG=false
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/plantassistant_test
CORS_ORIGINS=["http://localhost:3000"]
SECRET_KEY=test-secret-key-not-for-production
```

### Staging
```bash
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@staging-db:5432/plantassistant_staging
CORS_ORIGINS=["https://staging.yourapp.com"]
SECRET_KEY=staging-secret-key
```

### Production
```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/plantassistant
CORS_ORIGINS=["https://yourapp.com", "https://www.yourapp.com"]
SECRET_KEY=super-secure-production-secret-key
```

## 🚀 Quick Setup Commands

### Initialize Local Environment
```bash
# Copy example environment file
cp .env.example .env

# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start local database
make db-up

# Run migrations
make migrate

# Start development servers
make dev
```

### Validate Environment
```bash
# Check environment variables
make env-check

# Test database connection
make db-test

# Run full test suite
make test
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   make db-status
   
   # Check connection string
   echo $DATABASE_URL
   ```

2. **CORS Errors**
   ```bash
   # Verify CORS_ORIGINS includes your frontend URL
   echo $CORS_ORIGINS
   ```

3. **Secret Key Issues**
   ```bash
   # Generate new secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

---

💡 **Pro Tip**: Use different secret keys for each environment and rotate them regularly!

Create a `.env.local` file in the `frontend/` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000

# Environment
NODE_ENV=development
```

## Production Environment Variables

For production deployment, ensure you set:

- Strong `SECRET_KEY` (use `openssl rand -hex 32`)
- Production database URLs
- Real email server configuration
- `ENVIRONMENT=production`

## Security Notes

- Never commit `.env` files to version control
- Use environment-specific values
- Rotate secrets regularly
- Use strong, unique passwords for production
