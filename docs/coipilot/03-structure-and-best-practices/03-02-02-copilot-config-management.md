# Plant Assistant Config Management for GitHub Copilot

## Config Management
- Use .env files (dotenv for loading); never commit secrets (use .gitignore).
- Pydantic Settings for backend configs (e.g., class Settings(BaseSettings): DATABASE_URL: str).
- Frontend: process.env for env vars, .env.local for development.

## Detailed Practices
- Validation: Pydantic ensures types (e.g., str for keys).
- Secrets: Use vault services like AWS Secrets Manager for prod.

## Rationale
- Prevents leaks; easy environment switching (dev/prod).

## Scaling Considerations
- Add config validation in CI; use Kubernetes secrets for deployment.