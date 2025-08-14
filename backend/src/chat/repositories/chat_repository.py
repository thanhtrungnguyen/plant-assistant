"""
Chat Repository
Database operations for chat sessions, messages, and user profiles.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.models import (
    ChatSession,
    ChatMessage,
    MessageRole,
    UserPlantProfile,
    ChatFeedback,
)
from src.core.logging import get_logger

logger = get_logger(__name__)


class ChatRepository:
    """Repository for chat-related database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self, user_id: int, title: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid4())

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title=title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            total_messages=0,
            last_activity=datetime.now(timezone.utc),
            is_active=True,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        logger.debug(f"Created chat session {session_id} for user {user_id}")
        return session

    async def get_session(
        self, session_id: str, user_id: Optional[int] = None
    ) -> Optional[ChatSession]:
        """Get chat session by ID"""
        from sqlalchemy import select

        query = select(ChatSession).where(ChatSession.session_id == session_id)
        if user_id:
            query = query.where(ChatSession.user_id == user_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self, user_id: int, limit: int = 20, include_inactive: bool = False
    ) -> List[ChatSession]:
        """Get user's chat sessions"""
        from sqlalchemy import select

        query = select(ChatSession).where(ChatSession.user_id == user_id)

        if not include_inactive:
            query = query.where(ChatSession.is_active)

        query = query.order_by(desc(ChatSession.last_activity)).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        sequence_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """Add a message to chat session"""
        # Get session
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Auto-assign sequence number
        if sequence_number is None:
            sequence_number = session.total_messages + 1

        # Create message
        message = ChatMessage(
            session_id=session.id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            has_image=metadata.get("has_image", False) if metadata else False,
            plant_identified=metadata.get("plant_identified", False)
            if metadata
            else False,
            plant_species=metadata.get("plant_species") if metadata else None,
            confidence_score=metadata.get("confidence_score") if metadata else None,
            image_analysis=metadata.get("image_analysis") if metadata else None,
            model_used=metadata.get("model_used") if metadata else None,
            processing_time_ms=metadata.get("processing_time_ms") if metadata else None,
            embedding_id=metadata.get("embedding_id") if metadata else None,
        )

        self.db.add(message)

        # Update session
        session.total_messages += 1
        session.last_activity = datetime.now(timezone.utc)

        # Update session context if plant-related
        if metadata and metadata.get("plant_species"):
            if metadata["plant_species"] not in session.plant_species_mentioned:
                session.plant_species_mentioned.append(metadata["plant_species"])
                # Mark the column as dirty for SQLAlchemy to detect the change
                from sqlalchemy.orm.attributes import flag_modified

                flag_modified(session, "plant_species_mentioned")

        await self.db.commit()
        await self.db.refresh(message)

        logger.debug(f"Added message to session {session_id}: {role}")
        return message

    async def get_session_messages(
        self, session_id: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[ChatMessage]:
        """Get messages from a chat session"""
        from sqlalchemy import select

        # Get session first
        session = await self.get_session(session_id)
        if not session:
            return []

        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.sequence_number)
        )

        if offset > 0:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_context(
        self, session_id: str, message_count: int = 10
    ) -> List[ChatMessage]:
        """Get recent messages for context"""
        from sqlalchemy import select

        session = await self.get_session(session_id)
        if not session:
            return []

        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(desc(ChatMessage.sequence_number))
            .limit(message_count)
        )

        result = await self.db.execute(query)
        messages = list(result.scalars().all())

        # Return in chronological order
        return list(reversed(messages))

    async def create_or_update_user_profile(
        self, user_id: int, profile_data: Dict[str, Any]
    ) -> UserPlantProfile:
        """Create or update user plant profile"""
        from sqlalchemy import select

        # Check if profile exists
        query = select(UserPlantProfile).where(UserPlantProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()

        if profile:
            # Update existing profile
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
                    if key in [
                        "owned_plants",
                        "care_challenges",
                        "frequent_topics",
                        "successful_treatments",
                    ]:
                        from sqlalchemy.orm.attributes import flag_modified

                        flag_modified(profile, key)
        else:
            # Create new profile
            profile = UserPlantProfile(user_id=user_id, **profile_data)
            self.db.add(profile)

        await self.db.commit()
        await self.db.refresh(profile)

        logger.debug(f"Updated plant profile for user {user_id}")
        return profile

    async def get_user_profile(self, user_id: int) -> Optional[UserPlantProfile]:
        """Get user plant profile"""
        from sqlalchemy import select

        query = select(UserPlantProfile).where(UserPlantProfile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_session_context(
        self,
        session_id: str,
        plant_species: Optional[str] = None,
        plant_issue: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
    ):
        """Update session context for personalization"""
        session = await self.get_session(session_id)
        if not session:
            return

        updated = False

        if plant_species and plant_species not in session.plant_species_mentioned:
            session.plant_species_mentioned.append(plant_species)
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(session, "plant_species_mentioned")
            updated = True

        if plant_issue and plant_issue not in session.plant_issues_discussed:
            session.plant_issues_discussed.append(plant_issue)
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(session, "plant_issues_discussed")
            updated = True

        if user_preferences:
            session.user_preferences.update(user_preferences)
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(session, "user_preferences")
            updated = True

        if updated:
            session.last_activity = datetime.now(timezone.utc)
            await self.db.commit()
            logger.debug(f"Updated context for session {session_id}")

    async def add_feedback(
        self,
        message_id: int,
        user_id: int,
        rating: int,
        feedback_type: str,
        comment: Optional[str] = None,
    ) -> ChatFeedback:
        """Add feedback for a message"""
        feedback = ChatFeedback(
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
        )

        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)

        logger.debug(f"Added feedback for message {message_id}")
        return feedback

    async def get_user_interaction_stats(
        self, user_id: int, days: int = 30
    ) -> Dict[str, Any]:
        """Get user interaction statistics for personalization"""
        from sqlalchemy import select

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get sessions in date range
        sessions_query = select(ChatSession).where(
            and_(
                ChatSession.user_id == user_id, ChatSession.last_activity >= cutoff_date
            )
        )
        sessions_result = await self.db.execute(sessions_query)
        sessions = list(sessions_result.scalars().all())

        # Get messages in date range
        session_ids = [s.id for s in sessions]
        if not session_ids:
            return {}

        messages_query = select(ChatMessage).where(
            and_(
                ChatMessage.session_id.in_(session_ids),
                ChatMessage.created_at >= cutoff_date,
            )
        )
        messages_result = await self.db.execute(messages_query)
        messages = list(messages_result.scalars().all())

        # Calculate statistics
        plant_species = []
        plant_issues = []
        for session in sessions:
            plant_species.extend(session.plant_species_mentioned)
            plant_issues.extend(session.plant_issues_discussed)

        # Count frequencies
        from collections import Counter

        species_counter = Counter(plant_species)
        issues_counter = Counter(plant_issues)

        return {
            "total_sessions": len(sessions),
            "total_messages": len(messages),
            "frequent_plants": dict(species_counter.most_common(5)),
            "frequent_issues": dict(issues_counter.most_common(5)),
            "avg_messages_per_session": len(messages) / len(sessions)
            if sessions
            else 0,
            "last_activity": max(s.last_activity for s in sessions)
            if sessions
            else None,
        }

    async def cleanup_old_sessions(self, days_old: int = 90):
        """Clean up old inactive sessions"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)

        from sqlalchemy import select, delete

        # Find old sessions
        old_sessions_query = select(ChatSession.id).where(
            and_(ChatSession.last_activity < cutoff_date, ~ChatSession.is_active)
        )
        result = await self.db.execute(old_sessions_query)
        old_session_ids = [row[0] for row in result.fetchall()]

        if old_session_ids:
            # Delete messages first (due to foreign key constraints)
            await self.db.execute(
                delete(ChatMessage).where(ChatMessage.session_id.in_(old_session_ids))
            )

            # Delete sessions
            await self.db.execute(
                delete(ChatSession).where(ChatSession.id.in_(old_session_ids))
            )

            await self.db.commit()
            logger.info(f"Cleaned up {len(old_session_ids)} old chat sessions")

        return len(old_session_ids)
