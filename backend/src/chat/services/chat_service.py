"""Main chat service for managing conversations."""

import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.chat_message import MessageRole
from ..repositories.chat_repository import ChatRepository
from ..schemas import (
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatSessionWithMessages
)
from .rag_service import RAGService
from .langchain_service import LangChainChatService
from src.core.logging import get_logger

logger = get_logger(__name__)


class ChatService:
    """Main service for managing chat conversations."""

    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.rag_service = RAGService()
        self.langchain_service = LangChainChatService()

    async def process_chat_message(
        self,
        request: ChatRequest,
        user_id: int
    ) -> ChatResponse:
        """Process a chat message and generate response."""
        start_time = time.time()

        try:
            # Get or create session
            if request.session_id:
                session = await self.chat_repo.get_session_by_id(request.session_id, user_id)
                if not session:
                    raise ValueError(f"Session {request.session_id} not found")
            else:
                # Create new session with smart title generation
                title = await self._generate_session_title(request.message)
                session = await self.chat_repo.create_session(
                    user_id=user_id,
                    title=title,
                    related_plant_ids=[request.plant_id] if request.plant_id else None
                )

            # Store user message
            user_message = await self.chat_repo.create_message(
                session_id=session.id,
                role=MessageRole.USER,
                content=request.message,
                plant_context_ids=[request.plant_id] if request.plant_id else None,
                message_metadata={"context": request.context} if request.context else None
            )

            # Get conversation history for context
            recent_messages = await self.chat_repo.get_recent_messages(
                session_id=session.id,
                user_id=user_id,
                count=10
            )

            # Get RAG context if enabled
            retrieved_context = []
            if request.use_rag:
                try:
                    retrieved_context = await self.rag_service.get_relevant_context(
                        query=request.message,
                        plant_id=request.plant_id,
                        conversation_history=[msg.content for msg in recent_messages[-5:]]
                    )
                    logger.info(f"Retrieved {len(retrieved_context)} context items")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")

            # Generate response using LangChain
            response_data = await self.langchain_service.generate_response(
                message=request.message,
                conversation_history=recent_messages,
                retrieved_context=retrieved_context,
                plant_context_id=request.plant_id,
                user_context=request.context
            )

            # Store assistant message
            assistant_message = await self.chat_repo.create_message(
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content=response_data["message"],
                tokens_used=response_data.get("tokens_used"),
                processing_time=response_data.get("processing_time"),
                confidence_score=response_data.get("confidence"),
                retrieved_context=retrieved_context if retrieved_context else None,
                plant_context_ids=[request.plant_id] if request.plant_id else None,
                message_metadata={
                    "model_used": response_data.get("model_used"),
                    "suggestions": response_data.get("suggestions", []),
                    "related_actions": response_data.get("related_actions", [])
                }
            )

            # Update session activity
            await self.chat_repo.update_session_activity(session.id)

            total_processing_time = time.time() - start_time

            return ChatResponse(
                message=response_data["message"],
                session_id=session.id,
                message_id=assistant_message.id,
                suggestions=response_data.get("suggestions", []),
                related_actions=response_data.get("related_actions", []),
                confidence=response_data.get("confidence", 0.8),
                processing_time=total_processing_time,
                tokens_used=response_data.get("tokens_used"),
                retrieved_context=retrieved_context if retrieved_context else None
            )

        except Exception as e:
            logger.error(f"Chat processing failed: {e}")

            # Try to create a fallback response
            fallback_response = await self._create_fallback_response(
                request.message,
                session_id=request.session_id or 0
            )

            return ChatResponse(
                message=fallback_response,
                session_id=request.session_id or 0,
                message_id=0,
                suggestions=["Sorry, I encountered an error. Please try again."],
                related_actions=[],
                confidence=0.1,
                processing_time=time.time() - start_time,
                tokens_used=0
            )

    async def create_chat_session(
        self,
        session_data: ChatSessionCreate,
        user_id: int
    ) -> ChatSessionResponse:
        """Create a new chat session."""
        session = await self.chat_repo.create_session(
            user_id=user_id,
            title=session_data.title,
            user_preferences=session_data.user_preferences,
            related_plant_ids=session_data.related_plant_ids
        )

        return ChatSessionResponse.model_validate(session)

    async def get_user_sessions(
        self,
        user_id: int,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSessionResponse]:
        """Get user's chat sessions."""
        sessions = await self.chat_repo.get_user_sessions(
            user_id=user_id,
            active_only=active_only,
            limit=limit,
            offset=offset
        )

        return [ChatSessionResponse.model_validate(session) for session in sessions]

    async def get_session_with_messages(
        self,
        session_id: int,
        user_id: int,
        message_limit: Optional[int] = None
    ) -> Optional[ChatSessionWithMessages]:
        """Get session with its messages."""
        session = await self.chat_repo.get_session_with_messages(
            session_id=session_id,
            user_id=user_id,
            message_limit=message_limit
        )

        if not session:
            return None

        return ChatSessionWithMessages.model_validate(session)

    async def update_session(
        self,
        session_id: int,
        user_id: int,
        title: Optional[str] = None,
        is_active: Optional[bool] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        related_plant_ids: Optional[List[int]] = None
    ) -> Optional[ChatSessionResponse]:
        """Update a chat session."""
        updates = {}
        if title is not None:
            updates["title"] = title
        if is_active is not None:
            updates["is_active"] = is_active
        if user_preferences is not None:
            updates["user_preferences"] = user_preferences
        if related_plant_ids is not None:
            updates["related_plant_ids"] = related_plant_ids

        session = await self.chat_repo.update_session(session_id, user_id, **updates)

        if not session:
            return None

        return ChatSessionResponse.model_validate(session)

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        """Delete a chat session."""
        return await self.chat_repo.delete_session(session_id, user_id)

    async def get_chat_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get chat analytics for a user."""
        return await self.chat_repo.get_user_chat_stats(user_id)

    async def _generate_session_title(self, first_message: str) -> str:
        """Generate a smart title for the chat session based on the first message."""
        try:
            # Use LangChain service to generate title
            title = await self.langchain_service.generate_session_title(first_message)
            return title[:200]  # Ensure it fits in the database field
        except Exception as e:
            logger.warning(f"Failed to generate session title: {e}")
            # Fallback to simple truncation
            return first_message[:50] + "..." if len(first_message) > 50 else first_message

    async def _create_fallback_response(self, message: str, session_id: int) -> str:
        """Create a fallback response when main processing fails."""
        # Simple keyword-based fallback responses
        message_lower = message.lower()

        if any(word in message_lower for word in ["sick", "dying", "problem", "help"]):
            return "I'm sorry, I'm having trouble right now. For plant health issues, please consider consulting with a local plant expert or uploading a photo for visual diagnosis."

        if any(word in message_lower for word in ["water", "watering"]):
            return "I'm experiencing technical difficulties. Generally, most houseplants need watering when the top inch of soil feels dry. Please try your question again in a moment."

        if any(word in message_lower for word in ["light", "lighting", "sun"]):
            return "I'm currently unable to provide detailed advice. Most houseplants prefer bright, indirect light. Please try again shortly."

        return "I apologize, but I'm experiencing technical difficulties right now. Please try your question again in a few moments, or contact support if the issue persists."

    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old inactive sessions."""
        return await self.chat_repo.cleanup_old_sessions(days_old)
