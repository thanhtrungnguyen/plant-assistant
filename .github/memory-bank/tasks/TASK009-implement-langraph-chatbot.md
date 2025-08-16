# [TASK009] - Implement LangGraph-Powered Chatbo### 5. Service Layer Enhancemen### 8. Tool Implementation Details
- **8.1** **Diagnosis Tool**: Analyze plant images for health issues, provide solutions and recommendations

### 9. Testing & Validatio## Risks & Mitigation
- **API Costs**: Implement token usage monitoring and user quotas for both chat and context analysis
- **Response Latency**: Use streaming responses and caching for user context where appropriate
- **Diagnosis Service Failures**: Implement fallback mechanisms and error handling
- **Context Management**: Efficient conversation history loading and pruning to avoid token limits
- **Pinecone Costs**: Optimize user context updates to reduce vector database operations
- **Data Privacy**: Ensure user context summarization respects privacy and allows data deletion

## Progress Log
### 2025-08-16
- Created comprehensive task definition
- Analyzed existing database design and service integrations
- Defined implementation plan with detailed subtasks
- Identified technical specifications and success criteria
- **Simplified scope**: Focused on diagnosis tool integration only
- **Enhanced requirements**: Added chat history persistence, user context summarization with Pinecone `ChatService` to integrate with LangGraph agent
- **5.2** Implement conversation context management with database persistence
- **5.3** Add token usage tracking and cost monitoring
- **5.4** Implement streaming response capability
- **5.5** Add error handling and fallback mechanisms

### 6. Database Integration Enhancement
- **6.1** Enhance conversation session management with proper lifecycle handling
- **6.2** Implement advanced message persistence with metadata and search capabilities
- **6.3** Add conversation metadata support (source, locale, plant associations)
- **6.4** Implement user context data extraction from conversation history

### 7. API Enhancement Pending
**Added:** 2025-08-16
**Updated:** 2025-08-16

## Original Request
Create a chatbot implementation using LangGraph where we register tool nodes and plug the chatbot to those tools. The implementation should follow our database design with proper conversation management and integrate with existing plant-related services.

## Thought Process
The chatbot needs to be built as a LangGraph-powered conversational AI that can:

1. **Leverage Existing Database Design**: Use the `ConversationSession` and `ChatMessage` models from the conversations module (already aliased in chat/models.py)
2. **Chat History Management**: Maintain persistent conversation history in the database with proper session management
3. **Tool Integration**: Register tool nodes for plant diagnosis operations
4. **State Management**: Maintain conversation context and memory across interactions
5. **User Context Summarization**: Extract and store user context data (name, preferences, plant details) in Pinecone for personalized responses
6. **Streaming Support**: Provide real-time responses for better UX
7. **Cost Tracking**: Monitor token usage for OpenAI API calls

The implementation should integrate with existing services:
- Plant diagnosis (`src/diagnosis/`) - Primary tool for now
- Database models: `User`, `ConversationSession`, `ChatMessage`, `Plant`
- Vector database: Pinecone for user context storage

## Implementation Plan

### 1. LangGraph Core Architecture
- **1.1** Create LangGraph agent configuration with state management
- **1.2** Implement conversation state schema for context persistence
- **1.3** Set up graph nodes for different conversation flows
- **1.4** Configure memory management with Redis (future) or database persistence

### 2. Tool Node Registration
- **2.1** Create plant diagnosis tool node (integrate with existing diagnosis service)

### 3. Chat History & Conversation Management
- **3.1** Implement conversation session creation and management using existing `ConversationSession` model
- **3.2** Implement message persistence with `ChatMessage` model including token tracking
- **3.3** Create conversation history retrieval and context loading from database
- **3.4** Implement conversation threading and session continuity

### 4. User Context Summarization System
- **4.1** Create user context extraction service to analyze conversation patterns
- **4.2** Implement Pinecone integration for user context storage (name, preferences, plant info)
- **4.3** Create context summarization pipeline that updates user profile in vector database
- **4.4** Implement context retrieval for personalized responses based on user history

### 5. Service Layer Enhancement
- **3.1** Extend `ChatService` to integrate with LangGraph agent
- **3.2** Implement conversation context management
- **3.3** Add token usage tracking and cost monitoring
- **3.4** Implement streaming response capability
- **3.5** Add error handling and fallback mechanisms

### 4. Database Integration
- **4.1** Enhance conversation session management
- **4.2** Implement proper message persistence with token tracking
- **4.3** Add conversation metadata (source, locale, plant associations)
- **4.4** Implement conversation history retrieval and context loading

### 7. API Enhancement
- **7.1** Update chat routes to support LangGraph responses with chat history
- **7.2** Implement WebSocket support for real-time streaming
- **7.3** Add conversation management endpoints (list, retrieve, delete conversations)
- **7.4** Implement conversation export/import functionality
- **7.5** Add user context summary endpoints for debugging and management

### 8. Tool Implementation Details
- **6.1** **Diagnosis Tool**: Analyze plant images for health issues, provide solutions and recommendations

### 9. Testing & Validation
- **9.1** Unit tests for LangGraph agent configuration
- **9.2** Integration tests for diagnosis tool node functionality
- **9.3** Chat history persistence and retrieval testing
- **9.4** User context summarization and Pinecone integration testing
- **9.5** API endpoint testing with conversation flows
- **9.6** Performance testing for streaming responses
- **9.7** Cost monitoring and token usage validation

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | Create LangGraph agent configuration | Not Started | 2025-08-16 | Core agent setup with state management |
| 1.2 | Implement conversation state schema | Not Started | 2025-08-16 | Define state persistence structure |
| 1.3 | Set up graph nodes for conversation flows | Not Started | 2025-08-16 | Define conversation routing logic |
| 1.4 | Configure memory management | Not Started | 2025-08-16 | Context persistence strategy |
| 2.1 | Create plant diagnosis tool node | Not Started | 2025-08-16 | Integrate with existing diagnosis service |
| 3.1 | Implement conversation session management | Not Started | 2025-08-16 | Create/manage ConversationSession records |
| 3.2 | Implement message persistence system | Not Started | 2025-08-16 | Store ChatMessage with token tracking |
| 3.3 | Create conversation history retrieval | Not Started | 2025-08-16 | Load conversation context from database |
| 3.4 | Implement conversation threading | Not Started | 2025-08-16 | Session continuity and management |
| 4.1 | Create user context extraction service | Not Started | 2025-08-16 | Analyze conversations for user patterns |
| 4.2 | Implement Pinecone user context integration | Not Started | 2025-08-16 | Store user context in vector database |
| 4.3 | Create context summarization pipeline | Not Started | 2025-08-16 | Update user profiles from conversations |
| 4.4 | Implement personalized context retrieval | Not Started | 2025-08-16 | Use context for personalized responses |
| 5.1 | Extend ChatService for LangGraph integration | Not Started | 2025-08-16 | Core service enhancement |
| 5.2 | Implement conversation context management | Not Started | 2025-08-16 | Context loading and persistence |
| 5.3 | Add token usage tracking | Not Started | 2025-08-16 | Cost monitoring implementation |
| 5.4 | Implement streaming response capability | Not Started | 2025-08-16 | Real-time response streaming |
| 5.5 | Add error handling and fallback mechanisms | Not Started | 2025-08-16 | Robust error management |
| 6.1 | Enhance conversation session lifecycle | Not Started | 2025-08-16 | Advanced session handling |
| 6.2 | Implement advanced message persistence | Not Started | 2025-08-16 | Enhanced message storage with metadata |
| 6.3 | Add conversation metadata support | Not Started | 2025-08-16 | Source, locale, plant associations |
| 6.4 | Implement user context data extraction | Not Started | 2025-08-16 | Extract user info from chat history |
| 7.1 | Update chat routes for LangGraph with history | Not Started | 2025-08-16 | API endpoint enhancement |
| 7.2 | Implement WebSocket support | Not Started | 2025-08-16 | Real-time streaming API |
| 7.3 | Add conversation management endpoints | Not Started | 2025-08-16 | CRUD operations for conversations |
| 7.4 | Implement conversation export/import | Not Started | 2025-08-16 | Data portability features |
| 7.5 | Add user context summary endpoints | Not Started | 2025-08-16 | Debug and management endpoints |

## Technical Specifications

### LangGraph Configuration
```python
# Proposed agent configuration
class PlantAssistantAgent:
    def __init__(self):
        self.tools = [
            PlantDiagnosisTool()  # Only diagnosis tool for now
        ]
        self.memory = ConversationBufferMemory()
        self.graph = self._build_graph()
        self.user_context_service = UserContextService()
```

### Tool Node Interface
```python
class PlantDiagnosisTool:
    name: str = "plant_diagnosis"
    description: str = "Analyze plant images for health issues and provide solutions"

    async def execute(self, input_data: dict) -> dict:
        """Execute diagnosis with image analysis"""
        pass

    def get_schema(self) -> dict:
        """Return tool input schema for diagnosis"""
        pass
```

### User Context Summarization
```python
class UserContextService:
    def __init__(self, pinecone_client):
        self.pinecone = pinecone_client
        self.index = pinecone_client.Index("user-context")

    async def extract_user_context(self, user_id: int, messages: List[ChatMessage]) -> dict:
        """Extract user context from conversation history"""
        # Analyze messages for user name, preferences, plant details
        pass

    async def store_user_context(self, user_id: int, context: dict):
        """Store user context in Pinecone"""
        # Example: {"name": "John", "favorite_plants": ["roses"], "experience": "beginner"}
        pass

    async def get_user_context(self, user_id: int) -> dict:
        """Retrieve user context for personalization"""
        pass
```

### Chat History Management
```python
class ChatHistoryService:
    async def create_conversation_session(self, user_id: int, plant_id: int = None) -> ConversationSession:
        """Create new conversation session"""
        pass

    async def add_message(self, session_id: int, role: str, content: str, **metadata) -> ChatMessage:
        """Add message to conversation with token tracking"""
        pass

    async def get_conversation_history(self, session_id: int, limit: int = 50) -> List[ChatMessage]:
        """Retrieve conversation history"""
        pass

    async def get_user_conversations(self, user_id: int) -> List[ConversationSession]:
        """Get all user conversations"""
        pass
```

### Database Models
Using existing models from `src/conversations/models.py`:
- `ConversationSession`: Stores conversation metadata with user_id, plant_id, source, locale
- `ChatMessage`: Stores individual messages with token tracking (prompt/completion)
- `User`: User information including name for context summarization
- `Plant`: Plant information for conversation context

### Pinecone User Context Schema
```python
# Example user context stored in Pinecone
{
    "user_id": 123,
    "name": "John Doe",  # From User.name
    "experience_level": "beginner",  # Extracted from conversations
    "favorite_plants": ["roses", "orchids"],  # Extracted from conversations
    "plant_count": 5,  # Count of user's plants
    "common_issues": ["overwatering", "pest_problems"],  # Extracted from diagnosis history
    "preferred_language": "en",  # From conversation locale
    "last_updated": "2025-08-16T10:00:00Z"
}
```

### API Endpoints
- `POST /chat/conversation` - Send message and get response (creates session if needed)
- `GET /chat/conversations` - List user conversations with metadata
- `GET /chat/conversations/{id}/messages` - Get conversation history with pagination
- `DELETE /chat/conversations/{id}` - Delete conversation and all messages
- `GET /chat/user-context/{user_id}` - Get user context summary (debug endpoint)
- `WebSocket /chat/stream` - Real-time conversation streaming

## Dependencies
- **LangGraph**: State management and workflow orchestration
- **OpenAI API**: Language model and embeddings for chat and context analysis
- **Pinecone**: Vector database for user context storage and retrieval
- **Existing Diagnosis Service**: Plant health diagnosis functionality from `src/diagnosis/`
- **Database Models**: User, ConversationSession, ChatMessage, Plant from existing modules

## Success Criteria
1. **Functional Chatbot**: Users can have natural conversations about plant health issues
2. **Chat History**: Complete conversation history is stored and retrievable from database
3. **Persistent Sessions**: Conversations maintain context across sessions with proper session management
4. **User Context Personalization**: System learns and stores user context (name, preferences, experience) in Pinecone
5. **Personalized Responses**: Chatbot provides personalized responses based on user context and history
6. **Diagnosis Tool Integration**: Plant diagnosis tool is accessible and functional through chat interface
7. **Performance**: Response times under 3 seconds for text, 10 seconds for diagnosis tool use
8. **Cost Control**: Token usage tracking and monitoring implemented
9. **Error Handling**: Graceful degradation when services or APIs are unavailable
10. **Test Coverage**: Minimum 80% test coverage for all new components

## Risks & Mitigation
- **API Costs**: Implement token usage monitoring and user quotas
- **Response Latency**: Use streaming responses and caching where appropriate
- **Diagnosis Service Failures**: Implement fallback mechanisms and error handling
- **Context Management**: Efficient conversation history loading and pruning

## Progress Log
### 2025-08-16 - Initial Progress
- Created comprehensive task definition
- Analyzed existing database design and service integrations
- Defined implementation plan with detailed subtasks
- Identified technical specifications and success criteria
- **Simplified scope**: Focused on diagnosis tool integration only

### 2025-08-16 - Core Implementation Complete
- **✅ LangGraph Agent Architecture**: Implemented complete `PlantAssistantAgent` with state management and workflow orchestration
- **✅ State Management**: Created `ConversationState` with proper field tracking (messages, user context, tool results, token usage)
- **✅ Tool Integration**: Successfully integrated plant diagnosis tools with LangGraph ToolNode
- **✅ Conversation Workflow**: Built complete graph workflow with decision nodes for routing between chat and tool execution
- **✅ Memory Persistence**: Implemented MemorySaver checkpointing for conversation continuity
- **✅ User Context Service**: Built comprehensive `UserContextService` with Pinecone integration for user personalization
  - Conversation summarization using OpenAI
  - User context extraction and storage in vector database
  - Context retrieval for personalized responses
- **✅ Chat Service**: Developed complete `ChatService` with database integration
  - Message processing with LangGraph agent integration
  - Database persistence using correct ConversationSession/ChatMessage models
  - Conversation management (create, retrieve, delete)
  - Message history and user conversation listing
- **✅ API Routes**: Implemented full FastAPI integration
  - POST `/chat/message` - Send message and get response
  - GET `/chat/conversations` - List user conversations
  - GET `/chat/conversations/{id}/messages` - Get conversation history
  - DELETE `/chat/conversations/{id}` - Delete conversations
- **✅ Database Field Mapping**: Fixed all database field mappings to match existing schema
  - Used `session_id` instead of `conversation_session_id`
  - Used `created_at` instead of `timestamp`
  - Proper field mapping for all model interactions
- **✅ Model Configuration**: Updated to use proper settings
  - `settings.OPENAI_MODEL` for chat generation
  - `settings.OPENAI_EMBEDDING_MODEL` for RAG operations
  - Added missing `OPENAI_EMBEDDING_MODEL` setting to config
- **✅ Authentication Integration**: Integrated with existing `require_user` dependency
- **✅ Error Handling**: Comprehensive error handling and database transaction management
- **✅ Code Quality**: All lint errors resolved, proper typing and documentation

**Current Status**: Core implementation is complete and functional. All major components are implemented:
- LangGraph agent with tool integration ✅
- User context summarization with Pinecone ✅
- Chat service with database persistence ✅
- FastAPI routes with authentication ✅
- Proper database field mappings ✅
- Model configurations ✅

**Next Steps**:
- Integration testing with real database
- Frontend integration
- Performance optimization
- Token usage monitoring implementation
