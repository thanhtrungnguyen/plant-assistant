"""Repository for chat-related database operations."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc, func, and_, or_

from ..models.chat_session import ChatSession
from ..models.chat_message import ChatMessage, MessageRole


class ChatRepository:
    """Repository for managing chat sessions and messages."""

    def __init__(self, db: Session):
        self.db = db

    # Session management
    async def create_session(
        self,
        user_id: int,
        title: str = "New Chat",
        user_preferences: Optional[Dict[str, Any]] = None,
        related_plant_ids: Optional[List[int]] = None
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            user_id=user_id,
            title=title,
            user_preferences=user_preferences,
            related_plant_ids=related_plant_ids,
            last_activity=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    async def get_session_by_id(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        """Get a chat session by ID, ensuring user access."""
        return (
            self.db.query(ChatSession)
            .filter(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id
                )
            )
            .first()
        )

    async def get_user_sessions(
        self,
        user_id: int,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSession]:
        """Get user's chat sessions."""
        query = self.db.query(ChatSession).filter(ChatSession.user_id == user_id)

        if active_only:
            query = query.filter(ChatSession.is_active == True)

        return (
            query.order_by(desc(ChatSession.last_activity))
            .offset(offset)
            .limit(limit)
            .all()
        )

    async def update_session_activity(self, session_id: int) -> None:
        """Update session's last activity timestamp."""
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.last_activity = datetime.utcnow()
            self.db.commit()

    async def update_session(
        self,
        session_id: int,
        user_id: int,
        **updates
    ) -> Optional[ChatSession]:
        """Update a chat session."""
        session = await self.get_session_by_id(session_id, user_id)
        if not session:
            return None

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.last_activity = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session

    async def deactivate_session(self, session_id: int, user_id: int) -> bool:
        """Deactivate a chat session."""
        session = await self.get_session_by_id(session_id, user_id)
        if not session:
            return False

        session.is_active = False
        self.db.commit()
        return True

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        """Delete a chat session and all its messages."""
        session = await self.get_session_by_id(session_id, user_id)
        if not session:
            return False

        self.db.delete(session)
        self.db.commit()
        return True

    # Message management
    async def create_message(
        self,
        session_id: int,
        role: MessageRole,
        content: str,
        tokens_used: Optional[int] = None,
        processing_time: Optional[float] = None,
        confidence_score: Optional[float] = None,
        retrieved_context: Optional[List[Dict[str, Any]]] = None,
        plant_context_ids: Optional[List[int]] = None,
        message_metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            tokens_used=tokens_used,
            processing_time=processing_time,
            confidence_score=confidence_score,
            retrieved_context=retrieved_context,
            plant_context_ids=plant_context_ids,
            message_metadata=message_metadata
        )

        self.db.add(message)

        # Update session message count and activity
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.message_count += 1
            session.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    async def get_session_messages(
        self,
        session_id: int,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get messages for a session."""
        # Verify user has access to session
        session = await self.get_session_by_id(session_id, user_id)
        if not session:
            return []

        query = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    async def get_recent_messages(
        self,
        session_id: int,
        user_id: int,
        count: int = 10
    ) -> List[ChatMessage]:
        """Get recent messages from a session."""
        # Verify user has access to session
        session = await self.get_session_by_id(session_id, user_id)
        if not session:
            return []

        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(count)
            .all()
        )

    async def get_session_with_messages(
        self,
        session_id: int,
        user_id: int,
        message_limit: Optional[int] = None
    ) -> Optional[ChatSession]:
        """Get session with its messages."""
        session = (
            self.db.query(ChatSession)
            .options(selectinload(ChatSession.messages))
            .filter(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id
                )
            )
            .first()
        )

        if session and message_limit:
            # Limit messages if specified
            session.messages = session.messages[-message_limit:]

        return session

    # Analytics and statistics
    async def get_user_chat_stats(self, user_id: int) -> Dict[str, Any]:
        """Get chat statistics for a user."""
        total_sessions = (
            self.db.query(func.count(ChatSession.id))
            .filter(ChatSession.user_id == user_id)
            .scalar()
        )

        active_sessions = (
            self.db.query(func.count(ChatSession.id))
            .filter(
                and_(
                    ChatSession.user_id == user_id,
                    ChatSession.is_active == True
                )
            )
            .scalar()
        )

        total_messages = (
            self.db.query(func.count(ChatMessage.id))
            .join(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .scalar()
        )

        avg_messages_per_session = (
            self.db.query(func.avg(ChatSession.message_count))
            .filter(ChatSession.user_id == user_id)
            .scalar() or 0
        )

        avg_response_time = (
            self.db.query(func.avg(ChatMessage.processing_time))
            .join(ChatSession)
            .filter(
                and_(
                    ChatSession.user_id == user_id,
                    ChatMessage.role == MessageRole.ASSISTANT,
                    ChatMessage.processing_time.isnot(None)
                )
            )
            .scalar() or 0
        )

        return {
            "total_sessions": total_sessions or 0,
            "active_sessions": active_sessions or 0,
            "total_messages": total_messages or 0,
            "avg_messages_per_session": float(avg_messages_per_session),
            "avg_response_time": float(avg_response_time)
        }

    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old inactive sessions."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        deleted_count = (
            self.db.query(ChatSession)
            .filter(
                and_(
                    ChatSession.is_active == False,
                    ChatSession.last_activity < cutoff_date
                )
            )
            .delete()
        )

        self.db.commit()
        return deleted_count

    async def update_session_context_summary(
        self,
        session_id: int,
        summary: str
    ) -> None:
        """Update session context summary."""
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.context_summary = summary
            self.db.commit()
