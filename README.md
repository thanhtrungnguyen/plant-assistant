# Plant Assistant

<p align="center">
    <em>Plant Assistant: AI-powered plant care an## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest` (backend) and `pnpm test` (frontend)
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support

- 📧 **Issues**: [GitHub Issues](https://github.com/thanhtrungnguyen/plant-assistant/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/thanhtrungnguyen/plant-assistant/discussions)
- 📖 **Documentation**: Check the `docs/` directory for detailed guidest system built with Next.js and FastAPI.</em>
</p>
<p align="center">
<a href="https://github.com/thanhtrungnguyen/plant-assistant/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/thanhtrungnguyen/plant-assistant/actions/workflows/ci.yml/badge.svg" alt="CI">
</a>
<a href="https://coveralls.io/github/thanhtrungnguyen/plant-assistant" target="_blank">
    <img src="https://coveralls.io/repos/github/thanhtrungnguyen/plant-assistant/badge.svg" alt="Coverage">
</a>
</p>

---

**Repository**: <a href="https://github.com/thanhtrungnguyen/plant-assistant/" target="_blank">https://github.com/thanhtrungnguyen/plant-assistant/</a>

---

Plant Assistant is a comprehensive plant care and management application that helps users track, monitor, and care for their plants. Built with modern technologies including FastAPI, Next.js, and TypeScript, it provides a scalable foundation for plant enthusiasts and professionals.

### Key Features
✔ **Plant Management** – Track and organize your plant collection with detailed profiles

✔ **Care Scheduling** – Automated reminders for watering, fertilizing, and maintenance tasks

✔ **Health Monitoring** – Visual tracking of plant health and growth progress

✔ **User Authentication** – Secure user accounts with email verification and password recovery

✔ **Responsive Design** – Modern UI built with shadcn/ui and Tailwind CSS

✔ **Type Safety** – End-to-end type safety with TypeScript and Zod validation

## Technology Stack
This application uses modern, production-ready technologies:

- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Python 3.12 + UV package manager
- **Database**: PostgreSQL 17 with asyncpg
- **Authentication**: fastapi-users with JWT tokens
- **Validation**: Zod (frontend) + Pydantic (backend)
- **Development**: Docker Compose + Hot reload
- **Code Quality**: Pre-commit hooks + Ruff + ESLint
- **Deployment**: Vercel-ready configuration

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- pnpm
- Docker & Docker Compose

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/thanhtrungnguyen/plant-assistant.git
   cd plant-assistant
   ```

2. **Quick setup for new developers**
   ```bash
   make setup
   ```

3. **Start development environment**
   ```bash
   # With Docker (recommended)
   make dev

   # Or locally (requires Python 3.12+ and Node.js 20+)
   make dev-local
   ```

### Available Commands

Run `make help` to see all available commands:

```bash
make help
```

Key commands:
- `make dev` - Start full development environment
- `make test` - Run all tests
- `make lint` - Check code quality
- `make clean` - Clean build artifacts
- `make docs` - Start documentation server

## 📖 Documentation

- **[Backend Documentation](./backend/README.md)** - FastAPI setup, API endpoints, database management
- **[Frontend Documentation](./frontend/README.md)** - Next.js setup, UI components, styling guide
- **[Contributing Guidelines](./CONTRIBUTING.md)** - How to contribute to the project
- **[Environment Setup](./ENVIRONMENT.md)** - Environment variables and configuration
- **[Project Structure](./STRUCTURE.md)** - Detailed project architecture overview

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **MailHog (Email testing)**: http://localhost:8025

## 📁 Project Structure

This is a monorepo containing:

- **[`backend/`](./backend/README.md)** - FastAPI backend service with comprehensive API documentation
- **[`frontend/`](./frontend/README.md)** - Next.js frontend application with modern UI components
- **`docs/`** - Project documentation and guides
- **`local-shared-data/`** - Development data sharing between services

Each service has its own detailed README with specific setup instructions and architecture documentation.

## Using the template? Let's talk!

We’re always curious to see how the community builds on top of it and where it’s being used. To collaborate:

- Join the conversation on [GitHub Discussions](https://github.com/vintasoftware/nextjs-fastapi-template/discussions)
- Report bugs or suggest improvements via [issues](https://github.com/vintasoftware/nextjs-fastapi-template/issues)
- Check the [Contributing](https://vintasoftware.github.io/nextjs-fastapi-template/contributing/) guide to get involved

This project is maintained by [Vinta Software](https://www.vinta.com.br/) and is actively used in production systems we build for clients. Talk to our expert consultants — get a free technical review: contact@vinta.com.br.

*Disclaimer: This project is not affiliated with Vercel.*
