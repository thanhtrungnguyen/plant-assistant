# Plant Assistant Backend

FastAPI backend service for the Plant Assistant application, providing a robust API for plant care management, user authentication, and data persistence.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- UV package manager
- PostgreSQL (or use Docker Compose)

### Development Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run database migrations:**
   ```bash
   uv run alembic upgrade head
   ```

4. **Start the development server:**
   ```bash
   uv run fastapi dev src/app/main.py --host 0.0.0.0 --port 5000 --reload
   ```

5. **Access the API:**
   - API: http://localhost:5000
   - Interactive docs: http://localhost:5000/docs
   - OpenAPI spec: http://localhost:5000/openapi.json

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install/sync dependencies |
| `uv run fastapi dev src/app/main.py` | Start development server |
| `uv run pytest` | Run test suite |
| `uv run pytest --cov=src` | Run tests with coverage |
| `uv run ruff check` | Lint code |
| `uv run ruff format` | Format code |
| `uv run mypy src/` | Type checking |
| `uv run alembic upgrade head` | Apply database migrations |
| `uv run alembic revision --autogenerate` | Create new migration |

## 🏗️ Architecture

### Project Structure
```
backend/
├── src/app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── database.py          # Database setup and connection
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── users.py             # User authentication logic
│   ├── utils.py             # Utility functions
│   ├── routes/              # API endpoint definitions
│   │   └── items.py         # Plant-related endpoints
│   └── email_templates/     # Email template files
├── tests/                   # Test suite
├── alembic_migrations/      # Database migration files
├── commands/                # CLI commands
└── shared-data/             # Shared data with frontend
```

### Key Technologies
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization
- **fastapi-users**: Complete authentication system
- **AsyncPG**: Async PostgreSQL driver
- **Pytest**: Testing framework

## 🧪 Testing

### Run Tests
```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/test_main.py

# Watch mode
uv run pytest-watch
```

### Test Structure
- `tests/conftest.py` - Test configuration and fixtures
- `tests/test_*.py` - Test modules matching source structure
- `tests/main/` - API endpoint tests
- `tests/utils/` - Utility function tests

## 🗃️ Database

### Migrations
```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Check current version
uv run alembic current

# Migration history
uv run alembic history
```

### Models
- **User**: Authentication and user management
- **Item**: Plant/item management (extend as needed)

## 🔧 Development Tools

### Code Quality
```bash
# Linting
uv run ruff check

# Auto-fix issues
uv run ruff check --fix

# Code formatting
uv run ruff format

# Type checking
uv run mypy src/
```

### Generate OpenAPI Schema
```bash
uv run python -m commands.generate_openapi_schema
```

## 📧 Email Development

The application uses MailHog for email testing in development:
- Web interface: http://localhost:8025
- SMTP server: localhost:1025

## 🌍 Environment Variables

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `TEST_DATABASE_URL` | Test database connection | Required |
| `SECRET_KEY` | JWT signing key | Required |
| `MAIL_SERVER` | SMTP server host | `mailhog` |
| `MAIL_PORT` | SMTP server port | `1025` |
| `OPENAPI_OUTPUT_FILE` | OpenAPI schema output path | `./shared-data/openapi.json` |

## 🐳 Docker Development

```bash
# Start with Docker Compose
docker compose up backend

# Shell access
docker compose exec backend sh

# Run tests in container
docker compose exec backend pytest
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/jwt/login` - User login
- `POST /auth/jwt/logout` - User logout
- `POST /auth/register` - User registration
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset confirmation

### User Management
- `GET /users/me` - Current user profile
- `PATCH /users/me` - Update user profile

### Plant Management
- `GET /items/` - List user's plants
- `POST /items/` - Add new plant
- `GET /items/{id}` - Get plant details
- `PUT /items/{id}` - Update plant
- `DELETE /items/{id}` - Remove plant

## 🚀 Deployment

### Production Setup
1. Set production environment variables
2. Run database migrations
3. Use `fastapi run` instead of `fastapi dev`
4. Set up reverse proxy (nginx)
5. Configure SSL certificates

### Health Checks
The API includes health check endpoints for monitoring:
- Basic health: `GET /health` (if implemented)
- Database health: Check via any authenticated endpoint

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update this README for significant changes
4. Use type hints throughout
5. Follow PEP 8 style guidelines

### Adding New Endpoints
1. Define Pydantic schemas in `schemas.py`
2. Create route handlers in `routes/`
3. Include router in `main.py`
4. Add comprehensive tests
5. Update API documentation
