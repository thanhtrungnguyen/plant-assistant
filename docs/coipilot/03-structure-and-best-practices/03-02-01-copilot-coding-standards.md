# Plant Assistant Coding Standards for GitHub Copilot

## Coding Standards
- **Python**: Use type hints (mypy for checking), lint and format with Ruff (replaces Black/Flake8). Async for I/O-bound ops (e.g., API calls). Dependency injection in FastAPI (e.g., Depends for DB sessions).
  - Example: def get_db() -> Generator: yield SessionLocal()
- **JavaScript/TypeScript**: Hooks for state (useState), server components for data fetching. Format with Prettier, lint with ESLint (next/core-web-vitals extend).
  - Example: useEffect for side effects; interfaces for props.
- **General**: Modular code (one file per class/function), error handling (custom exceptions), input validation (Pydantic models for API payloads).

## Rationale
- Improves readability and reduces bugs (type hints catch 50% errors early).
- Tools Integration: Ruff in pre-commit hooks.

## Scaling Considerations
- Enforce with Husky for git hooks; add style guides in CONTRIBUTING.md.