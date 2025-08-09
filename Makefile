# Makefile

# Variables
BACKEND_DIR=backend
FRONTEND_DIR=frontend
DOCKER_COMPOSE=docker compose

# Help
.PHONY: help
help:
	@echo "Plant Assistant - Development Commands"
	@echo "====================================="
	@echo "Development:"
	@echo "  dev                  Start full development environment with Docker"
	@echo "  dev-local            Start development servers locally"
	@echo "  install              Install all dependencies"
	@echo "  clean                Clean all build artifacts"
	@echo ""
	@echo "Testing:"
	@echo "  test                 Run all tests"
	@echo "  test-backend         Run backend tests"
	@echo "  test-frontend        Run frontend tests"
	@echo "  test-coverage        Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint                 Run linting for both backend and frontend"
	@echo "  lint-fix             Fix linting issues"
	@echo "  format               Format code"
	@echo "  pre-commit                Run pre-commit hooks"
	@echo "  precommit-setup-windows   Setup pre-commit for Windows development"
	@echo "  precommit-setup-linux     Setup pre-commit for Linux/CI"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up            Start all services with Docker"
	@echo "  docker-down          Stop all Docker services"
	@echo "  docker-build         Build all Docker services"
	@echo "  docker-logs          Show logs from all services"
	@echo "  docker-clean         Clean Docker containers and volumes"
	@echo ""
	@echo "Database:"
	@echo "  migrate-db           Run database migrations"
	@echo "  db-schema            Generate new migration schema"
	@echo ""
	@echo "Utilities:"
	@echo "  setup                Complete setup for new developers"
	@echo "  quick-start          Quick start for development"
	@echo "  reset                Reset everything and reinstall"
	@echo "  docs                 Start documentation server"

# Development commands
.PHONY: dev dev-local dev-docker install clean lint

dev: docker-up ## Start full development environment with Docker

dev-local: ## Start development servers locally (requires local setup)
	@echo "Starting backend and frontend locally..."
	@echo "Backend: http://localhost:5000"
	@echo "Frontend: http://localhost:3000"
	@echo "Press Ctrl+C to stop both servers"
	@(cd $(BACKEND_DIR) && uv run fastapi dev src/app/main.py --host 0.0.0.0 --port 5000 --reload) & \
	(cd $(FRONTEND_DIR) && pnpm dev) & \
	wait

dev-docker: docker-up ## Start development environment with Docker

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd $(BACKEND_DIR) && uv sync
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && pnpm install

clean: ## Clean all build artifacts and dependencies
	@echo "Cleaning backend..."
	cd $(BACKEND_DIR) && rm -rf .venv __pycache__ .pytest_cache dist *.egg-info
	@echo "Cleaning frontend..."
	cd $(FRONTEND_DIR) && rm -rf .next node_modules .turbo dist

lint: ## Run linting for both backend and frontend
	@echo "Linting backend..."
	cd $(BACKEND_DIR) && uv run ruff check
	@echo "Linting frontend..."
	cd $(FRONTEND_DIR) && pnpm lint

lint-fix: ## Fix linting issues for both backend and frontend
	@echo "Fixing backend lint issues..."
	cd $(BACKEND_DIR) && uv run ruff check --fix
	@echo "Fixing frontend lint issues..."
	cd $(FRONTEND_DIR) && pnpm lint --fix

# Testing commands
.PHONY: test test-backend test-frontend test-coverage

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests using pytest
	cd $(BACKEND_DIR) && uv run pytest

test-frontend: ## Run frontend tests using pnpm
	cd $(FRONTEND_DIR) && pnpm run test

test-coverage: ## Run tests with coverage report
	@echo "Running backend tests with coverage..."
	cd $(BACKEND_DIR) && uv run pytest --cov=src --cov-report=html --cov-report=term
	@echo "Running frontend tests with coverage..."
	cd $(FRONTEND_DIR) && pnpm run coverage

# Backend commands
.PHONY: start-backend migrate-db db-schema

start-backend: ## Start the backend server with FastAPI and hot reload
	cd $(BACKEND_DIR) && uv run fastapi dev src/app/main.py --host 0.0.0.0 --port 5000 --reload

migrate-db: ## Run database migrations using Alembic
	cd $(BACKEND_DIR) && uv run alembic upgrade head

db-schema: ## Generate a new migration schema. Usage: make db-schema migration_name="add users"
	cd $(BACKEND_DIR) && uv run alembic revision --autogenerate -m "$(migration_name)"

# Frontend commands
.PHONY: start-frontend build-frontend

start-frontend: ## Start the frontend server with pnpm and hot reload
	cd $(FRONTEND_DIR) && pnpm dev

build-frontend: ## Build the frontend for production
	cd $(FRONTEND_DIR) && pnpm build


# Docker commands
.PHONY: docker-up docker-down docker-build docker-logs docker-clean \
        docker-backend-shell docker-frontend-shell docker-build-backend \
        docker-build-frontend docker-start-backend docker-start-frontend \
        docker-up-test-db docker-migrate-db docker-db-schema \
        docker-test-backend docker-test-frontend

docker-up: ## Start all services with Docker Compose
	$(DOCKER_COMPOSE) up --build

docker-down: ## Stop all Docker services
	$(DOCKER_COMPOSE) down

docker-build: ## Build all the services
	$(DOCKER_COMPOSE) build --no-cache

docker-logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Clean Docker containers, networks, and volumes
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f


docker-backend-shell: ## Access the backend container shell
	$(DOCKER_COMPOSE) run --rm backend sh

docker-frontend-shell: ## Access the frontend container shell
	$(DOCKER_COMPOSE) run --rm frontend sh

docker-build-backend: ## Build the backend container with no cache
	$(DOCKER_COMPOSE) build backend --no-cache

docker-build-frontend: ## Build the frontend container with no cache
	$(DOCKER_COMPOSE) build frontend --no-cache

docker-start-backend: ## Start the backend container
	$(DOCKER_COMPOSE) up backend

docker-start-frontend: ## Start the frontend container
	$(DOCKER_COMPOSE) up frontend

docker-up-test-db: ## Start the test database container
	$(DOCKER_COMPOSE) up db_test

docker-migrate-db: ## Run database migrations using Alembic
	$(DOCKER_COMPOSE) run --rm backend alembic upgrade head

docker-db-schema: ## Generate a new migration schema. Usage: make docker-db-schema migration_name="add users"
	$(DOCKER_COMPOSE) run --rm backend alembic revision --autogenerate -m "$(migration_name)"

docker-test-backend: ## Run tests for the backend
	$(DOCKER_COMPOSE) run --rm backend pytest

docker-test-frontend: ## Run tests for the frontend
	$(DOCKER_COMPOSE) run --rm frontend pnpm run test

# Utility commands
.PHONY: check-deps update-deps format pre-commit precommit-setup-windows precommit-setup-linux docs

check-deps: ## Check for dependency updates
	@echo "Checking backend dependencies..."
	cd $(BACKEND_DIR) && uv pip list --outdated
	@echo "Checking frontend dependencies..."
	cd $(FRONTEND_DIR) && pnpm outdated

update-deps: ## Update dependencies (use with caution)
	@echo "Updating backend dependencies..."
	cd $(BACKEND_DIR) && uv sync --upgrade
	@echo "Updating frontend dependencies..."
	cd $(FRONTEND_DIR) && pnpm update

format: ## Format code (backend and frontend)
	@echo "Formatting backend code..."
	cd $(BACKEND_DIR) && uv run ruff format
	@echo "Formatting frontend code..."
	cd $(FRONTEND_DIR) && pnpm run prettier

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

precommit-setup-windows: ## Setup pre-commit for Windows development
ifeq ($(OS),Windows_NT)
	powershell -ExecutionPolicy Bypass -File "./scripts/setup-precommit.ps1" -Windows
else
	./scripts/setup-precommit.sh windows
endif

precommit-setup-linux: ## Setup pre-commit for Linux/CI
ifeq ($(OS),Windows_NT)
	powershell -ExecutionPolicy Bypass -File "./scripts/setup-precommit.ps1" -Linux
else
	./scripts/setup-precommit.sh linux
endif

docs: ## Start documentation server
	mkdocs serve

# Shortcuts for common development tasks
.PHONY: setup quick-start reset

setup: install ## Complete setup for new developers
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo "Creating environment files..."
	@if [ ! -f $(BACKEND_DIR)/.env ]; then cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env; fi
	@echo "Setup complete! Run 'make dev' to start development."

quick-start: docker-up ## Quick start for development (Docker)

reset: clean docker-clean install ## Reset everything and reinstall
	@echo "Project reset complete!"