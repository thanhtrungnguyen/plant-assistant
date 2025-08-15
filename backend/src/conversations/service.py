"""Conversational AI service for plant assistance."""

import logging

from sqlalchemy.orm import Session

from src.conversations.models import ConversationSession, ChatMessage
from src.conversations.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ConversationSessionResponse,
    ChatHistoryMessage
)

logger = logging.getLogger(__name__)


class ConversationalService:
    """Service for handling conversational interactions about plants."""

    def __init__(self):
        """Initialize the conversational service."""
        pass

    async def get_chat_history(
        self, user_id: int, limit: int, offset: int, db: Session
    ) -> ChatHistoryResponse:
        """Get chat history for a specific user."""
        logger.info(f"Retrieving chat history for user {user_id}")

        # Get conversation sessions with pagination
        sessions_query = (
            db.query(ConversationSession)
            .filter(ConversationSession.user_id == user_id)
            .order_by(ConversationSession.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        sessions = sessions_query.all()

        # Get total count for pagination
        total_sessions = (
            db.query(ConversationSession)
            .filter(ConversationSession.user_id == user_id)
            .count()
        )

        # Build response with messages for each session
        session_responses = []
        for session in sessions:
            # Get messages for this session
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session.id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            # Convert messages to schema
            message_responses = [
                ChatHistoryMessage(
                    id=msg.id,
                    role=msg.role,
                    content_text=msg.content_text,
                    image_url=msg.image_url,
                    created_at=msg.created_at,
                )
                for msg in messages
            ]

            session_response = ConversationSessionResponse(
                id=session.id,
                started_at=session.started_at,
                ended_at=session.ended_at,
                messages=message_responses,
            )
            session_responses.append(session_response)

        return ChatHistoryResponse(
            sessions=session_responses,
            total_sessions=total_sessions,
        )


class ConversationalService:
    """Service for handling conversational interactions about plants."""

    def __init__(self):
        """Initialize the conversational service."""
        pass

    async def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and provide an intelligent response."""
        logger.info(f"Processing chat message: {request.message[:50]}...")

        # TODO: Implement conversational AI with:
        # - Intent recognition (OpenAI function calling)
        # - Context-aware responses
        # - Integration with other plant services
        # - Memory/session management

        # For now, provide a basic intelligent response
        message_lower = request.message.lower()

        if any(
            word in message_lower
            for word in ["sick", "dying", "brown", "yellow", "spots"]
        ):
            return ChatResponse(
                message="I can help you diagnose what might be wrong with your plant! It sounds like there might be an issue. Can you describe the symptoms in more detail or upload a photo?",
                suggestions=[
                    "Upload a photo for visual diagnosis",
                    "Describe the symptoms in detail",
                    "Tell me about your care routine",
                ],
                related_actions=["diagnose", "upload_photo"],
                confidence=0.85,
            )

        elif any(
            word in message_lower
            for word in ["care", "water", "light", "fertilize", "repot"]
        ):
            return ChatResponse(
                message="I'd be happy to help you with plant care! For personalized advice, I can consider your plant type, location, and environment. What specific aspect of care are you wondering about?",
                suggestions=[
                    "Get personalized care plan",
                    "Learn about watering schedules",
                    "Understand light requirements",
                ],
                related_actions=["care_advice", "create_plan"],
                confidence=0.9,
            )

        elif any(
            word in message_lower for word in ["identify", "what", "plant", "species"]
        ):
            return ChatResponse(
                message="I can help you identify your plant! You can upload up to 5 photos or describe it in detail. The more information you provide, the more accurate the identification will be.",
                suggestions=[
                    "Upload photos for identification",
                    "Describe the plant's features",
                    "Tell me where you found it",
                ],
                related_actions=["identify", "upload_photos"],
                confidence=0.9,
            )

        elif any(word in message_lower for word in ["reminder", "schedule", "forget"]):
            return ChatResponse(
                message="I can help you set up care reminders! You can create custom schedules for watering, fertilizing, repotting, and more. Would you like to set up some reminders?",
                suggestions=[
                    "Create watering reminders",
                    "Set fertilizer schedule",
                    "Plan repotting reminders",
                ],
                related_actions=["create_reminder", "schedule_care"],
                confidence=0.85,
            )

        else:
            return ChatResponse(
                message="Hi! I'm your plant care assistant. I can help you identify plants, diagnose problems, create care plans, and set up reminders. What would you like to know about your plants today?",
                suggestions=[
                    "Identify a plant from photos",
                    "Diagnose plant problems",
                    "Get personalized care advice",
                    "Set up care reminders",
                ],
                related_actions=["identify", "diagnose", "care_advice", "reminders"],
                confidence=0.7,
            )
