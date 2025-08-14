# 🤖 Hướng dẫn nâng cấp Chatbot

## 🎯 Vấn đề hiện tại
Chatbot chỉ trả lời được một số câu hỏi cơ bản vì đang sử dụng rule-based system với từ khóa cố định.

## 🚀 Giải pháp nâng cấp

### 1. **✅ Đã thực hiện: Chuyển sang Enhanced AI Endpoint**
- Frontend đã được cập nhật để sử dụng `/api/v2/chat/` thay vì `/chat/`
- Endpoint này sử dụng LangChain + LangGraph + OpenAI GPT

### 2. **🔧 Cần cấu hình: API Keys**

**Tạo file `.env` trong thư mục backend:**
```bash
# AI Services
OPENAI_API_KEY=your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here  # Optional: cho vector search

# OpenAI Configuration
OPENAI_MODEL=gpt-4o
OPENAI_VISION_MODEL=gpt-4o
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.1
```

**Lấy OpenAI API Key:**
1. Đăng ký tại: https://platform.openai.com/
2. Vào API Keys → Create new secret key
3. Copy key vào file .env

### 3. **🎯 Các tính năng AI sẽ có:**

**Trước khi có API key:**
- ❌ Chỉ trả lời từ khóa cố định
- ❌ Không hiểu ngữ cảnh
- ❌ Không học từ lịch sử

**Sau khi có API key:**
- ✅ Hiểu ngữ cảnh phức tạp
- ✅ Trả lời thông minh với AI
- ✅ Phân tích ảnh bằng GPT Vision
- ✅ Nhớ lịch sử hội thoại
- ✅ Cá nhân hóa phản hồi
- ✅ Tool calling (chẩn đoán chuyên sâu)

### 4. **🔄 Restart sau khi cấu hình**
```bash
# Restart backend để load API key
cd backend
uv run fastapi dev src/main.py --host 0.0.0.0 --port 5000
```

### 5. **🎨 Tùy chọn nâng cao khác:**

#### A. **Mở rộng Knowledge Base**
```python
# Thêm vào backend/src/chat/services/langchain_service.py
PLANT_CARE_KNOWLEDGE = {
    "succulents": "Cây mọng nước cần đất thoát nước tốt...",
    "ferns": "Dương xỉ thích ẩm độ cao...",
    "orchids": "Lan cần ánh sáng gián tiếp...",
    # Thêm nhiều kiến thức hơn
}
```

#### B. **Tích hợp thêm AI Services**
- **Google Gemini**: Thay thế OpenAI
- **Anthropic Claude**: Cho phân tích phức tạp
- **Local LLM**: Ollama cho privacy

#### C. **Vector Database cho tìm kiếm**
- **Pinecone**: Cloud vector DB
- **Chroma**: Local vector DB
- **FAISS**: Fast similarity search

#### D. **Multi-modal AI**
- **GPT-4 Vision**: Phân tích ảnh
- **DALL-E**: Tạo ảnh minh họa
- **Whisper**: Nhận dạng giọng nói

### 6. **📊 Metrics & Analytics**
- Theo dõi độ hài lòng user
- Thống kê câu hỏi phổ biến
- A/B test different AI models

### 7. **🛡️ Safety & Moderation**
- Content filtering
- Rate limiting
- User authentication

## 🎯 Bước tiếp theo ngay lập tức:

1. **Tạo file `.env` với OpenAI API key**
2. **Restart backend**
3. **Test chatbot với câu hỏi phức tạp**

Sau đó chatbot sẽ thông minh hơn rất nhiều! 🧠✨
