"""
Chat Service - Plant Care Assistant

Provides conversational AI interface for plant care assistance,
with optional integration to plant diagnosis service for image analysis.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# from app.services.plant_diagnosis import PlantDiagnosisService, get_diagnosis_service
from .schemas import ChatMessage, ChatRequest


class ChatService:
    """Plant care chat assistant service"""

    def __init__(self):
        # self.diagnosis_service = diagnosis_service
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())

    def _get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """Get existing session or create new one"""
        if session_id and session_id in self._sessions:
            self._sessions[session_id]["updated_at"] = datetime.now()
            return session_id

        new_session_id = self._generate_session_id()
        self._sessions[new_session_id] = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "messages": [],
            "message_count": 0,
        }
        return new_session_id

    def _add_message_to_session(self, session_id: str, message: ChatMessage):
        """Add message to session history"""
        if session_id in self._sessions:
            self._sessions[session_id]["messages"].append(message.dict())
            self._sessions[session_id]["message_count"] += 1
            self._sessions[session_id]["updated_at"] = datetime.now()

    def _get_plant_care_response(
        self, message: str, conversation_history: List[ChatMessage]
    ) -> Dict[str, Any]:
        """Generate plant care response based on message and context"""

        # Common plant care keywords and responses
        keywords_responses = {
            "watering": {
                "message": "🌱 Tưới nước là yếu tố quan trọng! Hầu hết cây trồng cần đất ẩm nhưng không úng nước. Kiểm tra độ ẩm đất bằng cách nhấn ngón tay xuống đất 2-3cm. Nếu khô thì cần tưới.",
                "suggestions": [
                    "Làm sao kiểm tra độ ẩm đất?",
                    "Tần suất tưới nước cho cây trong nhà?",
                    "Dấu hiệu cây bị úng nước?",
                ],
            },
            "ánh sáng": {
                "message": "☀️ Ánh sáng là nguồn năng lượng cho cây! Hầu hết cây trong nhà cần ánh sáng gián tiếp, tránh ánh nắng trực tiếp. Đặt cây gần cửa sổ hướng đông hoặc bắc là tốt nhất.",
                "suggestions": [
                    "Cây nào chịu được ánh sáng yếu?",
                    "Dấu hiệu cây thiếu ánh sáng?",
                    "Có nên dùng đèn LED cho cây?",
                ],
            },
            "phân bón": {
                "message": "🌿 Phân bón cung cấp dinh dưỡng cho cây! Mùa xuân-hè bón 2 tuần/lần, mùa đông giảm bớt. Dùng phân NPK cân bằng hoặc phân hữu cơ.",
                "suggestions": [
                    "Loại phân nào tốt cho cây trong nhà?",
                    "Dấu hiệu cây thiếu dinh dưỡng?",
                    "Bón phân quá nhiều có hại không?",
                ],
            },
            "bệnh": {
                "message": "🔍 Phát hiện bệnh sớm rất quan trọng! Các triệu chứng thường gặp: lá vàng, đốm nâu, lá héo, rệp. Hãy gửi ảnh để tôi chẩn đoán cụ thể hơn!",
                "suggestions": [
                    "Cách phòng ngừa bệnh cho cây?",
                    "Thuốc trừ sâu nào an toàn?",
                    "Tôi có thể gửi ảnh chẩn đoán không?",
                ],
            },
            "vàng lá": {
                "message": "🍂 Lá vàng có thể do nhiều nguyên nhân:\n\n💧 **Tưới nước không đúng**: Quá nhiều hoặc quá ít\n☀️ **Thiếu ánh sáng**: Cây không đủ năng lượng\n🌿 **Thiếu dinh dưỡng**: Đặc biệt là nitơ\n🌡️ **Stress môi trường**: Thay đổi nhiệt độ, ẩm độ\n\nHãy kiểm tra từng yếu tố này!",
                "suggestions": [
                    "Cách kiểm tra độ ẩm đất?",
                    "Loại phân bón nào tốt?",
                    "Tôi cần gửi ảnh chẩn đoán",
                ],
            },
            "héo": {
                "message": "🥀 Cây héo thường do:\n\n💧 **Thiếu nước**: Đất quá khô\n🌡️ **Quá nóng**: Nhiệt độ cao, ẩm độ thấp\n🦠 **Bệnh rễ**: Do úng nước lâu ngày\n⚡ **Shock**: Thay đổi môi trường đột ngột\n\nKiểm tra đất và môi trường ngay!",
                "suggestions": [
                    "Cách cứu cây bị héo?",
                    "Phân biệt thiếu nước và úng nước?",
                    "Tôi muốn gửi ảnh cây",
                ],
            },
        }

        # Check for keywords in message
        message_lower = message.lower()
        for keyword, response in keywords_responses.items():
            if keyword in message_lower:
                return response

        # Default response for general plant care questions
        if any(
            word in message_lower for word in ["cây", "trồng", "chăm sóc", "lá", "hoa"]
        ):
            return {
                "message": "🌱 Tôi có thể giúp bạn chăm sóc cây trồng! Hãy cho tôi biết cụ thể bạn cần hỗ trợ gì: tưới nước, ánh sáng, phân bón, hay chẩn đoán bệnh? Bạn cũng có thể gửi ảnh cây để tôi phân tích chi tiết.",
                "suggestions": [
                    "Cách tưới nước đúng cách?",
                    "Cây tôi bị vàng lá, nguyên nhân gì?",
                    "Chẩn đoán bệnh qua ảnh",
                    "Phân bón nào tốt cho cây trong nhà?",
                ],
            }

        # Generic greeting or conversation
        if any(word in message_lower for word in ["xin chào", "hello", "hi", "chào"]):
            return {
                "message": "Xin chào! 👋 Tôi là trợ lý chăm sóc cây trồng. Tôi có thể giúp bạn:\n\n🔍 Chẩn đoán bệnh cây qua ảnh\n💧 Tư vấn tưới nước\n☀️ Hướng dẫn ánh sáng\n🌿 Tư vấn phân bón\n\nBạn cần hỗ trợ gì ạ?",
                "suggestions": [
                    "Chẩn đoán bệnh qua ảnh",
                    "Hướng dẫn tưới nước",
                    "Tư vấn ánh sáng cho cây",
                    "Cách bón phân đúng cách",
                ],
            }

        # Default response
        return {
            "message": "Tôi hiểu bạn đang cần hỗ trợ! Tôi chuyên về chăm sóc cây trồng. Bạn có thể:\n\n📸 Gửi ảnh cây để chẩn đoán\n❓ Hỏi về tưới nước, ánh sáng, phân bón\n🌱 Tư vấn chăm sóc cây cụ thể\n\nHãy mô tả vấn đề hoặc gửi ảnh nhé!",
            "suggestions": [
                "Tôi muốn chẩn đoán cây qua ảnh",
                "Cây của tôi có vấn đề gì đó",
                "Hướng dẫn chăm sóc cây cơ bản",
            ],
        }

    async def process_chat(self, request: ChatRequest) -> Dict[str, Any]:
        """Process chat request and return response"""
        try:
            # Get or create session
            session_id = self._get_or_create_session(request.session_id)

            # Add user message to session
            user_message = ChatMessage(
                role="user", content=request.message, timestamp=datetime.now()
            )
            self._add_message_to_session(session_id, user_message)

            # If image provided, suggest diagnosis (for now just acknowledge)
            if request.image_base64:
                response_data = {
                    "message": "📸 Tôi đã nhận được ảnh của bạn! Hiện tại tính năng phân tích ảnh tự động đang được phát triển.\n\n� **Tạm thời, hãy mô tả:**\n• Loại cây gì?\n• Triệu chứng bạn thấy?\n• Lá có vàng, héo, đốm không?\n• Cây có sâu bệnh không?\n\nTôi sẽ tư vấn dựa trên mô tả của bạn!",
                    "suggestions": [
                        "Cây bị vàng lá",
                        "Cây bị héo",
                        "Có sâu bệnh trên lá",
                        "Cây không phát triển",
                    ],
                    "plant_identified": False,
                }
            else:
                # Text-only conversation
                response_data = self._get_plant_care_response(
                    request.message, request.conversation_history or []
                )

            # Add assistant message to session
            assistant_message = ChatMessage(
                role="assistant",
                content=response_data["message"],
                timestamp=datetime.now(),
            )
            self._add_message_to_session(session_id, assistant_message)

            # Return response
            return {
                "message": response_data["message"],
                "session_id": session_id,
                "timestamp": datetime.now(),
                "suggestions": response_data.get("suggestions", []),
                "plant_identified": response_data.get("plant_identified"),
                "confidence_score": response_data.get("confidence_score"),
            }

        except Exception as e:
            return {
                "error": "processing_error",
                "message": f"Lỗi xử lý chat: {str(e)}",
                "session_id": request.session_id,
            }


# Dependency injection
_chat_service: Optional[ChatService] = None


async def get_chat_service() -> ChatService:
    """Get chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
