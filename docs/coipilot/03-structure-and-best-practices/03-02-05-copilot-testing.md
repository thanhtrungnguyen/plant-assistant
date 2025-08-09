# Plant Assistant Testing for GitHub Copilot

## Testing
- **Unit**: Services/agents (pytest for backend with fixtures; Jest for frontend mocks).
- **Integration**: End-to-end API calls (supertest for FastAPI, Cypress for UI).
- Coverage: Aim for 80% (coverage.py, istanbul).

## Detailed Strategy
- TDD Approach: Write tests first for critical paths (e.g., ID accuracy).
- Mocks: Mock OpenAI calls for determinism.

## Rationale
- Catches bugs early; ensures AI reliability.

## Scaling Considerations
- Add e2e tests with Playwright; CI for auto-testing.