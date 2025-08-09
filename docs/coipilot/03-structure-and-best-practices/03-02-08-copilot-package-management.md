# Plant Assistant Package Management for GitHub Copilot

## Package Management
- **Backend (UV)**: Fast installs/resolution. Commands: `uv add fastapi`, `uv sync`, `uv run uvicorn src.main:app --reload`. uv.lock for reproducibility. In Docker: Install UV, then sync.
- **Frontend (Shadcn UI)**: PNPM for management. Commands: `pnpm install`, `pnpm add axios`, `pnpm dev`. pnpm-lock.yaml for locks. Init Next.js: `npx create-next-app@latest`. Shadcn: `npx shadcn-ui@latest init`, add via `npx shadcn-ui@latest add button`. Tailwind: Customize in tailwind.config.js.

## Benefits
- UV: 10x faster than pip. PNPM: Saves space, faster installs.

## Rationale
- Reproducible builds; easy dep updates.

## Scaling Considerations
- Add workspaces if monorepo; audit deps with Snyk.