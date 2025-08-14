# Enhanced Chat System với Personalization

## Tổng quan

Hệ thống chat đã được nâng cấp với các tính năng cá nhân hóa mạnh mẽ sử dụng PostgreSQL và Pinecone vector database.

## Tính năng chính

### 🤖 Personalization với AI
- **Học từ lịch sử**: Hệ thống nhớ các cây bạn đã hỏi và vấn đề thường gặp
- **Phong cách giao tiếp**: Tự động điều chỉnh theo trình độ (beginner/expert)
- **Context memory**: Sử dụng Pinecone để lưu trữ và tìm kiếm ngữ cảnh liên quan
- **Continuous learning**: Học từ feedback để cải thiện câu trả lời

### 📚 Persistent Storage
- **PostgreSQL**: Lưu trữ lịch sử chat, user profiles, feedback
- **Session management**: Quản lý phiên chat liên tục
- **Plant tracking**: Theo dõi cây trồng và vấn đề của từng user

### 🔍 Vector Search với Pinecone
- **Semantic search**: Tìm kiếm ngữ cảnh liên quan dựa trên ý nghĩa
- **Knowledge base**: Lưu trữ kiến thức chăm sóc cây dạng vector
- **User context**: Lưu profile và interaction patterns

## Cấu trúc Database

### Chat Tables
```sql
-- Chat sessions
chat_sessions
├── id (PK)
├── session_id (unique)
├── user_id (FK)
├── title
├── total_messages
├── last_activity
├── plant_species_mentioned (JSON)
├── plant_issues_discussed (JSON)
└── user_preferences (JSON)

-- Chat messages
chat_messages
├── id (PK)
├── session_id (FK)
├── role (user/assistant)
├── content
├── sequence_number
├── plant_identified
├── plant_species
├── confidence_score
├── has_image
├── embedding_id (Pinecone reference)
└── created_at

-- User plant profiles
user_plant_profiles
├── id (PK)
├── user_id (FK, unique)
├── experience_level
├── preferred_language
├── communication_style
├── owned_plants (JSON)
├── care_challenges (JSON)
├── frequent_topics (JSON)
└── successful_treatments (JSON)

-- Chat feedback
chat_feedback
├── id (PK)
├── message_id (FK)
├── user_id (FK)
├── rating (1-5)
├── feedback_type
├── comment
└── created_at
```

## API Endpoints

### Enhanced Chat Endpoints

#### `POST /chat/`
Gửi tin nhắn với personalization
```json
{
  "message": "Cây của tôi bị vàng lá",
  "image_base64": "optional_base64_image",
  "session_id": "optional_session_id"
}
```

Response:
```json
{
  "message": "Dựa trên cây kim tiền bạn đã hỏi trước đây...",
  "session_id": "session_123",
  "suggestions": ["Kiểm tra độ ẩm đất", "Thay đổi vị trí"],
  "plant_identified": true,
  "personalization_used": true
}
```

#### `GET /chat/sessions`
Lấy danh sách chat sessions
```json
{
  "sessions": [
    {
      "session_id": "session_123",
      "title": "Chăm sóc kim tiền",
      "total_messages": 15,
      "plant_species_mentioned": ["kim tiền", "cây cọ"]
    }
  ]
}
```

#### `GET /chat/sessions/{session_id}`
Lấy tin nhắn trong session
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Cây kim tiền bị vàng lá",
      "plant_identified": true,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### `POST /chat/feedback`
Gửi feedback để cải thiện
```json
{
  "message_id": 123,
  "rating": 5,
  "feedback_type": "helpful",
  "comment": "Lời khuyên rất hữu ích!"
}
```

## Setup và Cài đặt

### 1. Cài đặt Dependencies
```bash
cd backend
uv add pinecone-client openai numpy scikit-learn
```

### 2. Environment Variables
Thêm vào `.env`:
```env
# OpenAI
OPENAI_API_KEY=sk-proj-your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=plant-assistant-knowledge
PINECONE_DIMENSION=1536

# Chat Config
PERSONALIZATION_ENABLED=true
CHAT_CONTEXT_WINDOW=10
```

### 3. Database Migration
```bash
uv run alembic revision --autogenerate -m "Add chat tables"
uv run alembic upgrade head
```

### 4. Pinecone Setup
1. Tạo account tại [pinecone.io](https://pinecone.io)
2. Tạo index với dimension=1536 (cho text-embedding-3-small)
3. Cập nhật API key và index name

## Sử dụng

### Basic Chat với Personalization
```python
from src.chat.enhanced_service import get_chat_service

# Khởi tạo service
chat_service = await get_chat_service(db)

# Gửi tin nhắn
response = await chat_service.process_chat(
    request=ChatRequest(message="Cây của tôi bị héo"),
    user_id=123
)
```

### Quản lý User Profile
```python
# Cập nhật profile
await chat_service.chat_repo.create_or_update_user_profile(
    user_id=123,
    profile_data={
        "experience_level": "beginner",
        "owned_plants": ["kim tiền", "cọ"],
        "care_challenges": ["tưới nước", "ánh sáng"]
    }
)
```

### Vector Search với Pinecone
```python
from src.chat.services.pinecone_service import get_pinecone_service

pinecone_service = await get_pinecone_service()

# Tìm context liên quan
contexts = await pinecone_service.search_relevant_context(
    query="cây bị vàng lá",
    user_id=123,
    top_k=5
)
```

## Monitoring và Analytics

### Performance Metrics
- Response time tracking
- Personalization effectiveness
- User satisfaction scores
- Knowledge base coverage

### Usage Analytics
```python
# Thống kê user interaction
stats = await chat_service.chat_repo.get_user_interaction_stats(
    user_id=123,
    days=30
)

print(f"Tổng sessions: {stats['total_sessions']}")
print(f"Cây thường hỏi: {stats['frequent_plants']}")
```

## Tối ưu hóa

### Database Performance
- Index trên user_id, session_id, created_at
- Pagination cho large datasets
- Cleanup old data tự động

### Pinecone Cost Optimization
- Batch upserts
- Cleanup old vectors
- Smart caching strategies

### Memory Management
- Lazy loading of context
- Connection pooling
- Background processing

## Security

### Data Privacy
- User data encryption
- Secure API keys
- Rate limiting
- Access control per user

### Vector Database Security
- Namespace isolation per user
- Metadata filtering
- API key rotation

## Troubleshooting

### Common Issues

1. **Pinecone Connection Errors**
   - Kiểm tra API key và index name
   - Verify dimension compatibility

2. **Database Migration Issues**
   - Backup database trước khi migrate
   - Check PostgreSQL connection

3. **Performance Issues**
   - Monitor Pinecone query latency
   - Check database query performance
   - Optimize context window size

### Debug Commands
```bash
# Test Pinecone connection
uv run python -c "from src.chat.services.pinecone_service import get_pinecone_service; import asyncio; asyncio.run(get_pinecone_service())"

# Test database connection
uv run python -c "from src.database.session import engine; print('DB connected')"

# Check migration status
uv run alembic current
```

## Roadmap

### Phase 1 (Completed) ✅
- Basic personalization
- PostgreSQL integration
- Pinecone setup
- Enhanced chat API

### Phase 2 (Planned)
- Machine learning recommendations
- Advanced analytics dashboard
- Multi-language support
- Voice chat integration

### Phase 3 (Future)
- Real-time notifications
- Community features
- Expert consultation booking
- IoT sensor integration
