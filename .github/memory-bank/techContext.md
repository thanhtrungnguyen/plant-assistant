# Technology Context

## Core Technology Stack

### Backend Technologies
**FastAPI (Python 3.12+)**
- **Why chosen**: High-performance async framework with automatic OpenAPI documentation
- **Key benefits**: Type hints integration, excellent async support, built-in data validation
- **Usage patterns**: RESTful API endpoints, dependency injection, background tasks
- **Configuration**: UV package manager for dependency management

**SQLAlchemy + AsyncPG**
- **Why chosen**: Mature ORM with excellent async support and type safety
- **Usage**: Database models with typed mappings (`Mapped[int]` for IDs)
- **Migration strategy**: Alembic for schema management
- **Connection pooling**: Async connection pools for performance

**PostgreSQL 17**
- **Why chosen**: Robust relational database with JSON support and strong consistency
- **Usage**: Primary data store for users, plants, care logs, and structured data
- **Features utilized**: JSONB columns for flexible plant attributes, full-text search

**Pinecone Vector Database**
- **Why chosen**: Fully managed vector database with excellent performance and scalability
- **Usage**: Store plant care knowledge embeddings for AI-powered recommendations
- **Integration**: OpenAI embeddings for plant data semantic search and retrieval
- **Benefits**: Cloud-native with automatic scaling, built-in metadata filtering, production-ready

**Redis (Future)**
- **Planned usage**: Session storage, caching, background task queuing
- **Why**: High-performance caching and pub/sub capabilities
- **Integration**: AsyncIO-compatible Python client

### AI & Machine Learning
**OpenAI API**
- **Models used**: GPT-4o for text processing, Vision API for image analysis
- **Cost considerations**: Token usage monitoring and per-user quotas
- **Fallback strategy**: Graceful degradation when API unavailable
- **Integration**: LangChain/LangGraph for complex workflows

**LangGraph**
- **Why chosen**: Stateful AI workflow orchestration with graph-based logic
- **Usage**: Multi-step plant identification and care advice workflows
- **Benefits**: Better than simple LangChain for complex reasoning chains
- **State management**: Redis for conversation persistence

**Embeddings Pipeline**
- **Strategy**: OpenAI text-embedding-3-small for plant care knowledge vectorization
- **Storage**: Pinecone index with namespace organization and metadata filtering
- **Query**: Semantic search for relevant plant care information with similarity scoring

### Frontend Technologies
**Next.js 15**
- **Why chosen**: React framework with excellent developer experience and performance
- **Features used**: App Router, Server Components, API routes
- **Deployment**: Vercel-optimized with automatic deployments
- **Performance**: Automatic code splitting and image optimization

**TypeScript**
- **Usage**: End-to-end type safety from database to UI
- **Integration**: Auto-generated API client from OpenAPI schema
- **Development**: Strict type checking with comprehensive interfaces

**Tailwind CSS + shadcn/ui**
- **Why chosen**: Utility-first CSS with high-quality component library
- **Benefits**: Rapid development, consistent design system, accessibility built-in
- **Customization**: Custom color schemes and component variants

**Form Handling**
- **React Hook Form**: Performant forms with minimal re-renders
- **Zod**: Schema validation matching backend Pydantic models
- **Integration**: Type-safe form validation with error handling

### Development Tools

**Package Management**
- **Backend**: UV (modern Python package manager, faster than pip/poetry)
- **Frontend**: pnpm (efficient node_modules management with workspace support)
- **Benefits**: Fast installs, consistent dependency resolution, monorepo support

**Code Quality**
- **Backend**: Ruff (fast linting and formatting), MyPy (type checking)
- **Frontend**: ESLint (linting), Prettier (formatting), TypeScript compiler
- **Pre-commit hooks**: Automated code quality checks before commits

**Testing Frameworks**
- **Backend**: Pytest with async support, coverage reporting, test fixtures
- **Frontend**: Jest + React Testing Library for component and integration tests
- **API Testing**: Automated tests against OpenAPI specification

**Database Management**
- **Alembic**: Database migrations with version control
- **Development**: Docker Compose with persistent volumes
- **Testing**: Separate test database with automatic cleanup

### Infrastructure & Deployment

**Containerization**
- **Docker**: Multi-stage builds for production optimization
- **Docker Compose**: Development environment orchestration
- **Container registry**: Deployment-ready images with health checks

**Environment Management**
- **Configuration**: Environment-specific .env files with validation
- **Secrets**: Secure handling of API keys and database credentials
- **Validation**: Pydantic Settings for configuration parsing and validation

**Monitoring & Observability**
- **Logging**: Structured JSON logging with correlation IDs
- **Health checks**: API endpoints for service monitoring
- **Error tracking**: Exception logging with context information
- **Performance**: Response time tracking and database query monitoring

### External Integrations

**Email System**
- **Development**: MailHog for local email testing
- **Production**: SendGrid or similar SMTP service for transactional emails
- **Templates**: Jinja2 templates for email formatting

**Weather Integration (Future)**
- **OpenWeather API**: Environmental data for care recommendations
- **Geolocation**: IP-based location detection for local weather
- **Caching**: Weather data caching to reduce API calls

**Plant Databases (Future)**
- **USDA Plant Database**: Authoritative plant information and hardiness zones
- **Integration**: API clients for plant data enrichment
- **Fallback**: Local plant database for offline operation

## Technical Constraints

### Performance Requirements
- **API Response Time**: <500ms for standard operations, <2s for AI operations
- **Concurrent Users**: Support 1,000+ concurrent users without degradation
- **Database**: Efficient queries with proper indexing and connection pooling
- **Caching**: Multi-level caching strategy (Redis, CDN, browser)

### Security Requirements
- **Authentication**: JWT tokens with secure key management
- **API Security**: Rate limiting, input validation, SQL injection prevention
- **Data Privacy**: GDPR compliance for EU users, data encryption at rest
- **File Upload**: Secure image processing with virus scanning and size limits

### Scalability Considerations
- **Stateless Design**: Horizontal scaling with load balancers
- **Database**: Read replicas for scaling read operations
- **Background Tasks**: Queue-based processing for non-blocking operations
- **AI Processing**: Rate limiting and cost controls for external APIs

### Development Constraints
- **Python Version**: 3.12+ for latest async and type hint features
- **Node Version**: 22+ for latest Next.js features and performance improvements
- **Browser Support**: Modern browsers (last 2 versions), mobile-first responsive design
- **Accessibility**: WCAG 2.1 AA compliance for all UI components

## Configuration Management

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/plant_assistant
TEST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/plant_assistant_test

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENAI_API_KEY=your-openai-key
WEATHER_API_KEY=your-weather-key

# Email
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Dependency Versions
- **Python**: ^3.12
- **FastAPI**: ^0.104.0
- **SQLAlchemy**: ^2.0.0
- **Node.js**: ^22.0.0
- **Next.js**: ^15.0.0
- **React**: ^18.0.0

This technology stack provides a modern, scalable foundation for the Plant Assistant application while maintaining developer productivity and system reliability.
