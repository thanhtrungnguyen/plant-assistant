"""
Demo script to create sample chat history data for testing.
Run this script to populate the database with sample conversation sessions and messages.
"""

import asyncio
from datetime import datetime, timedelta
from src.database.session import get_db
from src.conversations.models import ConversationSession, ChatMessage

# Sample conversation data
SAMPLE_CONVERSATIONS = [
    {
        "user_id": 1,  # Assuming user with ID 1 exists
        "started_at": datetime.now() - timedelta(days=3),
        "messages": [
            {
                "role": "user",
                "content": "Xin chào! Tôi có một cây monstera và nó có vấn đề gì đó.",
            },
            {
                "role": "assistant",
                "content": "Chào bạn! Tôi rất sẵn lòng giúp bạn với cây Monstera. Bạn có thể mô tả chi tiết vấn đề bạn đang gặp không? Ví dụ như lá có vàng, nâu hay có dấu hiệu bệnh nào khác?",
            },
            {
                "role": "user",
                "content": "Lá của nó bắt đầu vàng và có một số lá bị nâu ở mép.",
            },
            {
                "role": "assistant",
                "content": "Dựa vào mô tả của bạn, có thể cây đang gặp vấn đề về tưới nước. Lá vàng thường là dấu hiệu tưới quá nhiều hoặc thoát nước kém. Bạn có thể kiểm tra độ ẩm của đất và đảm bảo chậu có lỗ thoát nước tốt không?",
            },
        ],
    },
    {
        "user_id": 1,
        "started_at": datetime.now() - timedelta(days=1),
        "messages": [
            {
                "role": "user",
                "content": "Tôi muốn hỏi về việc bón phân cho cây cảnh trong nhà.",
            },
            {
                "role": "assistant",
                "content": "Việc bón phân cho cây cảnh trong nhà rất quan trọng! Bạn đang trồng loại cây nào? Thông thường, cây cảnh trong nhà cần bón phân vào mùa xuân và hè (mùa sinh trưởng) với tần suất 2-4 tuần/lần.",
            },
            {"role": "user", "content": "Tôi có cây pothos và cây snake plant."},
            {
                "role": "assistant",
                "content": "Cả hai loại cây này đều rất dễ chăm sóc! Pothos thích phân bón cân bằng NPK, bón 1 lần/tháng vào mùa sinh trưởng. Snake plant ít cần phân hơn, có thể bón 2-3 tháng/lần. Nhớ pha loãng phân bón theo hướng dẫn để tránh bỏng rễ nhé!",
            },
        ],
    },
    {
        "user_id": 1,
        "started_at": datetime.now() - timedelta(hours=2),
        "messages": [
            {
                "role": "user",
                "content": "Cây của tôi có côn trùng nhỏ màu xanh trên lá, đó là gì?",
            },
            {
                "role": "assistant",
                "content": "Nghe có vẻ như cây của bạn bị rệp xanh (aphids)! Đây là loại côn trùng hút nhựa cây rất phổ biến. Bạn có thể xử lý bằng cách: 1) Xịt nước mạnh để cuốn trôi rệp, 2) Dùng dung dịch xà phòng pha loãng, 3) Hoặc sử dụng dầu neem. Bạn có thể chụp ảnh để tôi xác định chính xác hơn không?",
            },
        ],
    },
]


async def create_sample_data():
    """Create sample chat history data."""
    # Get database session
    db_gen = get_db()
    db = next(db_gen)

    try:
        print("Creating sample conversation sessions...")

        for conv_data in SAMPLE_CONVERSATIONS:
            # Create conversation session
            session = ConversationSession(
                user_id=conv_data["user_id"],
                started_at=conv_data["started_at"],
                source="web",
                locale="vi-VN",
            )
            db.add(session)
            db.flush()  # To get the session ID

            print(f"Created session {session.id}")

            # Create messages for this session
            for i, msg_data in enumerate(conv_data["messages"]):
                message = ChatMessage(
                    session_id=session.id,
                    role=msg_data["role"],
                    content_text=msg_data["content"],
                    created_at=conv_data["started_at"] + timedelta(minutes=i * 2),
                )
                db.add(message)

            print(
                f"Added {len(conv_data['messages'])} messages to session {session.id}"
            )

        # Commit all changes
        db.commit()
        print("✅ Sample data created successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(create_sample_data())
