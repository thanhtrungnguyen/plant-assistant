# System Patterns

## Architecture Overview

### High-Level Architecture
The application follows a modern **monolithic-first approach** with clear service boundaries for future microservice extraction if needed. The architecture emphasizes:

- **Separation of concerns** between frontend, backend, and data layers
- **Domain-driven design** with clear module boundaries
- **API-first design** with comprehensive OpenAPI documentation
- **Event-driven patterns** for notifications and background processing

### System Topology
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│   Services      │
│                 │    │                  │    │                 │
│ • React UI      │    │ • REST API       │    │ • OpenAI API    │
│ • State Mgmt    │    │ • Authentication │    │ • Weather API   │
│ • API Client    │    │ • Business Logic │    │ • USDA Plant DB │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌─────────▼──────────┐
                       │   Data Layer       │
                       │                    │
                       │ • PostgreSQL       │
                       │ • Chroma Vector DB │
                       │ • Redis Cache      │
                       └────────────────────┘
```

## Core Design Patterns

### 1. Repository Pattern (Backend)
Abstracts data access logic with clear interfaces:

```python
# Abstract base repository
class BaseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]
    
    @abstractmethod 
    async def create(self, data: CreateSchema) -> T

# Concrete implementations
class PlantRepository(BaseRepository[Plant, PlantCreate]):
    async def get_by_id(self, id: UUID) -> Optional[Plant]:
        # SQLAlchemy implementation
        
class PlantCacheRepository(BaseRepository[Plant, PlantCreate]):
    async def get_by_id(self, id: UUID) -> Optional[Plant]:
        # Redis cache implementation with fallback
```

### 2. Service Layer Pattern
Business logic encapsulation with clear dependencies:

```python
class PlantService:
    def __init__(
        self, 
        plant_repo: PlantRepository,
        ai_service: AIService,
        notification_service: NotificationService
    ):
        self.plant_repo = plant_repo
        self.ai_service = ai_service
        self.notification_service = notification_service
    
    async def identify_plant(self, user_id: UUID, images: List[str]) -> PlantIdentification:
        # Orchestrates AI identification with database persistence
        # Handles business rules and error scenarios
```

### 3. Dependency Injection (FastAPI)
Clean dependency management using FastAPI's dependency injection:

```python
# Dependencies defined in dependencies.py
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # JWT validation and user retrieval

async def get_plant_service(
    plant_repo: PlantRepository = Depends(get_plant_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> PlantService:
    return PlantService(plant_repo, ai_service)

# Clean route handlers
@router.post("/plants/identify")
async def identify_plant(
    request: IdentifyRequest,
    user: User = Depends(get_current_user),
    plant_service: PlantService = Depends(get_plant_service)
):
    return await plant_service.identify_plant(user.id, request.images)
```

### 4. Event-Driven Patterns
Asynchronous processing for notifications and background tasks:

```python
# Event system using Python's asyncio and APScheduler
class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable):
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: Event):
        for handler in self._handlers[event.type]:
            await handler(event)

# Usage
event_bus.subscribe("plant.health_changed", send_health_notification)
event_bus.subscribe("care.reminder_due", send_care_reminder)
```

### 5. Strategy Pattern (AI Processing)
Flexible AI processing with multiple providers:

```python
class AIStrategy(ABC):
    @abstractmethod
    async def identify_plant(self, images: List[str]) -> PlantIdentification:
        pass

class OpenAIStrategy(AIStrategy):
    async def identify_plant(self, images: List[str]) -> PlantIdentification:
        # OpenAI Vision implementation

class LocalModelStrategy(AIStrategy):
    async def identify_plant(self, images: List[str]) -> PlantIdentification:
        # Local TensorFlow model implementation

class AIService:
    def __init__(self, strategy: AIStrategy):
        self._strategy = strategy
    
    async def identify_plant(self, images: List[str]) -> PlantIdentification:
        return await self._strategy.identify_plant(images)
```

## Data Flow Patterns

### 1. Request-Response Flow
```
Client → Middleware → Route → Service → Repository → Database
       ←           ←       ←         ←            ←
```

### 2. Background Processing Flow
```
API Request → Event Published → Background Worker → External API → Database Update → User Notification
```

### 3. Caching Strategy
```
Request → Cache Check → Database Query (if miss) → Cache Update → Response
```

## Component Relationships

### Frontend Architecture (Next.js)
- **Pages**: App Router with file-based routing
- **Components**: Reusable UI components with shadcn/ui
- **Hooks**: Custom React hooks for state management
- **Services**: API client with auto-generated types
- **Utils**: Shared utility functions and validation

### Backend Architecture (FastAPI)
- **Routes**: API endpoint definitions with OpenAPI documentation
- **Services**: Business logic and orchestration
- **Models**: SQLAlchemy database models with type hints
- **Schemas**: Pydantic models for request/response validation
- **Dependencies**: Reusable dependency injection components
- **Utils**: Shared utilities and helper functions

### Key Architectural Decisions

1. **Monolith First**: Single deployable unit for MVP, with clear module boundaries for future extraction
2. **API-First**: Backend exposes comprehensive REST API with OpenAPI spec
3. **Type Safety**: End-to-end type safety with TypeScript and Pydantic
4. **Async-First**: Asynchronous operations throughout for scalability
5. **Modular Design**: Clear separation of concerns enabling independent development
6. **Event-Driven**: Decoupled components communicating through events
7. **Configuration-Based**: Environment-specific behavior through configuration files
8. **Testing-Friendly**: Dependency injection and interfaces enable comprehensive testing

### Scalability Considerations

1. **Horizontal Scaling**: Stateless services with external session storage
2. **Database Optimization**: Read replicas and connection pooling
3. **Caching Strategy**: Multi-level caching (Redis, CDN, browser)
4. **Background Processing**: Queue-based task processing with worker pools
5. **Microservice Ready**: Clear service boundaries for future extraction
6. **Monitoring**: Comprehensive logging and metrics collection
7. **Feature Flags**: Gradual rollout and A/B testing capabilities

This architecture provides a solid foundation for the MVP while maintaining flexibility for future growth and feature additions.
