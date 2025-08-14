# Plant Assistant Deployment and Infra for GitHub Copilot

## Deployment/Infra
- **Docker**: Consistent envs; volumes for data persistence (e.g., postgres_data).
- **CI/CD**: GitHub Actions for tests/lints (e.g., workflow on push).
- **Scalability**: Monitor OpenAI costs (prom-client); horizontal scaling with load balancers.

## Detailed Setup
- Compose YML: Services for postgres, Pinecone, backend (uv run uvicorn), frontend (pnpm dev).
- Deployment: Vercel for frontend, Render for backend.

## Rationale
- Prod-like local setup reduces "works on my machine" issues.

## Scaling Considerations
- Move to Kubernetes; add auto-scaling based on traffic.
