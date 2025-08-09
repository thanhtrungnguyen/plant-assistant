# Contributing to Plant Assistant

Thank you for your interest in contributing to Plant Assistant! We welcome contributions from the community.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/plant-assistant.git
   cd plant-assistant
   ```

3. Set up the development environment:
   ```bash
   # With Docker (recommended)
   docker compose up --build

   # Or locally
   cd backend && uv sync
   cd ../frontend && pnpm install
   ```

## Code Standards

### Backend (Python/FastAPI)
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for public methods
- Maintain test coverage above 80%

### Frontend (Next.js/TypeScript)
- Use TypeScript for all new code
- Follow the established component patterns
- Use Tailwind CSS for styling
- Ensure responsive design

## Testing

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## Pre-commit Hooks

This project uses pre-commit hooks with dual platform support:

### Setup for Your Platform
```bash
# For Windows local development
make precommit-setup-windows

# For Linux/CI (GitHub Actions)  
make precommit-setup-linux
```

### Install and Run
```bash
# Install hooks (one time)
pre-commit install

# Run on all files
make pre-commit
```

See [docs/precommit-setup.md](docs/precommit-setup.md) for detailed configuration guide.

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request with a clear description

## Code Review Guidelines

- PRs require at least one approval
- All CI checks must pass
- Keep PRs focused and reasonably sized
- Write clear commit messages

## Reporting Issues

When reporting issues, please include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node versions)
- Relevant logs or error messages

## Questions?

Feel free to open a discussion or issue if you have questions!
