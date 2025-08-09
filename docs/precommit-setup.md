# Dual Pre-commit Configuration Guide

This project supports development on both Windows and Linux/CI environments with dual pre-commit configurations.

## Quick Setup

### For Windows Local Development
```bash
make precommit-setup-windows
# or
.\scripts\setup-precommit.ps1 -Windows
```

### For Linux/CI (GitHub Actions)
```bash
make precommit-setup-linux
# or
./scripts/setup-precommit.sh linux
```

## Configuration Files

- **`.pre-commit-config.yaml`** - Active configuration (defaults to Linux for CI compatibility)
- **`.pre-commit-config.windows.yaml`** - Windows PowerShell commands for local development
- **`.pre-commit-config.linux.yaml`** - Linux sh commands for CI/GitHub Actions

## Platform Differences

### Windows Configuration
- Uses PowerShell commands
- Optimized for local Windows development
- Frontend commands: `cd frontend; pnpm run lint`
- Backend commands: `cd backend; uv run ruff check`

### Linux Configuration  
- Uses sh commands with `-c` flag
- Required for GitHub Actions CI
- Frontend commands: `sh -c "cd frontend && pnpm run lint"`
- Backend commands: `sh -c "cd backend && uv run ruff check"`

## Development Workflow

1. **Initial Setup**: Install pre-commit hooks
   ```bash
   pre-commit install
   ```

2. **Configure for Your Platform**:
   - Windows: `make precommit-setup-windows`
   - Linux: `make precommit-setup-linux`

3. **Run Pre-commit**:
   ```bash
   make pre-commit
   # or
   pre-commit run --all-files
   ```

## Continuous Integration

The GitHub Actions workflows automatically use the Linux configuration. The default `.pre-commit-config.yaml` is set to the Linux version to ensure CI compatibility.

## Commands Available

All commands available through both Makefile and direct scripts:

- `make pre-commit` - Run pre-commit on all files
- `make precommit-setup-windows` - Switch to Windows config  
- `make precommit-setup-linux` - Switch to Linux config
- `.\scripts\setup-precommit.ps1 -Help` - Show PowerShell script help
- `./scripts/setup-precommit.sh help` - Show bash script help

## Checks Performed

Both configurations run the same quality checks:

1. **Frontend** (in `frontend/` directory):
   - ESLint with TypeScript rules
   - TypeScript type checking
   - Prettier formatting
   - OpenAPI client generation

2. **Backend** (in `backend/` directory):  
   - Ruff linting and formatting
   - MyPy type checking
   - OpenAPI schema generation

3. **General**:
   - Trailing whitespace removal
   - End-of-file fixing
   - YAML syntax checking

## Troubleshooting

- **PowerShell Execution Policy**: The scripts use `-ExecutionPolicy Bypass` to avoid issues
- **Path Resolution**: Both configs use absolute paths for cross-platform compatibility
- **pnpm Workspace**: Frontend commands properly handle pnpm workspace structure

## Best Practices

1. Run `make precommit-setup-windows` when developing locally on Windows
2. The Linux config is used automatically in CI - no manual intervention needed
3. Always run `make pre-commit` before committing to catch issues early
4. Both configurations ensure the same code quality standards across platforms
