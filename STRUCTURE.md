# Project Structure

```
plant-assistant/
├── .github/                    # GitHub-specific files
│   ├── workflows/             # CI/CD workflows
│   ├── dependabot.yml         # Dependency updates
│   └── PULL_REQUEST_TEMPLATE.md
├── .devcontainer/             # VS Code dev container config
├── backend/                   # FastAPI backend
│   ├── src/
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py        # FastAPI app entry point
│   │       ├── config.py      # App configuration
│   │       ├── database.py    # Database setup
│   │       ├── models.py      # SQLAlchemy models
│   │       ├── schemas.py     # Pydantic schemas
│   │       ├── users.py       # User management
│   │       ├── utils.py       # Utility functions
│   │       └── routes/        # API routes
│   ├── tests/                 # Backend tests
│   ├── alembic_migrations/    # Database migrations
│   ├── commands/              # Management commands
│   ├── pyproject.toml         # Python dependencies
│   ├── Dockerfile            # Backend container config
│   └── start.sh              # Container startup script
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js 13+ app directory
│   │   ├── components/        # React components
│   │   └── lib/              # Utility libraries
│   ├── public/               # Static assets
│   ├── __tests__/            # Frontend tests
│   ├── package.json          # Node.js dependencies
│   ├── Dockerfile           # Frontend container config
│   └── tailwind.config.js    # Tailwind CSS config
├── docs/                     # Project documentation
├── local-shared-data/        # Development data sharing
├── overrides/               # Template overrides
├── docker-compose.yml       # Development environment
├── Makefile                 # Build automation
├── mkdocs.yml              # Documentation site config
├── package.json            # Root workspace config
├── README.md               # Project overview
├── CONTRIBUTING.md         # Contribution guidelines
├── ENVIRONMENT.md          # Environment setup guide
└── LICENSE.txt             # License file
```

## Directory Purpose

### `/backend`
Contains the FastAPI application with:
- **API routes**: REST endpoints for plant management
- **Database models**: SQLAlchemy ORM models
- **Authentication**: User management and JWT handling
- **Business logic**: Core plant care algorithms
- **Tests**: Comprehensive test suite

### `/frontend`
Next.js application featuring:
- **Pages**: App router-based page structure
- **Components**: Reusable UI components with shadcn/ui
- **API client**: Auto-generated TypeScript client
- **State management**: React hooks and context
- **Styling**: Tailwind CSS with custom components

### `/docs`
MkDocs-powered documentation:
- **User guides**: How to use the application
- **API documentation**: Endpoint references
- **Development guides**: Setup and contribution info
- **Deployment**: Production deployment guides

### Configuration Files

- **`docker-compose.yml`**: Multi-service development environment
- **`.pre-commit-config.yaml`**: Code quality automation
- **`Makefile`**: Build and deployment commands
- **`mkdocs.yml`**: Documentation site configuration

## Development Workflow

1. **Feature Development**: Work in feature branches
2. **Testing**: Run tests locally before pushing
3. **Code Quality**: Pre-commit hooks ensure standards
4. **Documentation**: Update docs for new features
5. **Review**: Pull request review process
6. **Deployment**: Automated deployment on merge

## Best Practices

- **Separation of concerns**: Backend handles business logic, frontend handles presentation
- **Type safety**: TypeScript throughout, Pydantic validation
- **Testing**: Comprehensive test coverage for both frontend and backend
- **Documentation**: Keep docs updated with code changes
- **Security**: Environment variables, authentication, input validation
