"""Chat service with LangGraph integration and database persistence."""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from src.chat.agent import PlantAssistantAgent
from src.chat.services.context_service import UserContextService
from src.conversations.models import ConversationSession, ChatMessage

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat operations with LangGraph integration."""

    def __init__(self, db: AsyncSession):
        """Initialize the chat service."""
        self.db = db
        self.agent = PlantAssistantAgent()
        self.context_service = UserContextService()

    async def process_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None,
        plant_id: Optional[int] = None,
        image_data: Optional[str] = None
    ) -> Dict:
        """Process a chat message and return the response."""
        try:
            # Get or create conversation session
            if conversation_id:
                try:
                    conv_id = int(conversation_id)
                    conversation = await self._get_conversation(conv_id, user_id)
                    if not conversation:
                        raise ValueError(f"Conversation {conversation_id} not found")
                except ValueError:
                    raise ValueError(f"Invalid conversation_id format: {conversation_id}")
            else:
                conversation = await self._create_conversation(user_id, plant_id)
                conversation_id = str(conversation.id)  # Use database ID as conversation_id

            # Retrieve relevant user context before processing
            logger.info(f"Retrieving user context for user {user_id}")
            user_context = await self.context_service.retrieve_user_context(
                user_id=user_id,
                current_message=message,
                top_k=3  # Get top 3 most relevant context entries
            )

            # Format context for the agent as a dictionary
            context_dict = None
            if user_context:
                # Filter for highly relevant context only
                relevant_context = [ctx for ctx in user_context if ctx.get("relevance_score", 0) > 0.6]

                if relevant_context:
                    # Extract the most recent context about plant diagnosis/identification
                    most_recent_context = relevant_context[0]  # Highest relevance score
                    recent_summary = most_recent_context.get("summary", "")

                    # Try to parse plant information from the summary
                    most_recent_plant = self._extract_plant_info_from_summary(recent_summary)

                    context_dict = {
                        "most_recent_plant": most_recent_plant,
                        "context_summary": recent_summary,
                        "recent_conversations": [ctx.get("summary", "") for ctx in relevant_context[:3]],
                        "total_context_entries": len(user_context),
                        "relevant_entries": len(relevant_context)
                    }
                    logger.info(f"Using context for response: {len(relevant_context)} relevant entries")

            # Store user message
            user_message = ChatMessage(
                session_id=conversation.id,
                role="user",
                content_text=message,
                image_url=image_data,  # Base64 image data if provided
                created_at=datetime.utcnow()
            )
            self.db.add(user_message)
            await self.db.flush()

            # Process with agent (including user context)
            agent_response = await self.agent.process_message(
                user_id=str(user_id),
                message=message,
                conversation_id=conversation_id,
                plant_id=str(plant_id) if plant_id else None,
                image_data=image_data,  # Pass image data to agent
                user_context=context_dict  # Pass context dictionary to agent
            )

            # Store assistant response
            assistant_message = ChatMessage(
                session_id=conversation.id,
                role="assistant",
                content_text=agent_response["response"],
                model=agent_response.get("model"),
                token_prompt=agent_response.get("input_tokens"),
                token_completion=agent_response.get("output_tokens"),
                created_at=datetime.utcnow()
            )
            self.db.add(assistant_message)
            await self.db.flush()  # Ensure ID is available
            await self.db.commit()

            # Process conversation for context storage (async background task)
            # This runs after successful message processing to update user context
            try:
                # Check if this is a substantial conversation (more than basic greeting)
                if len(message.split()) > 2 or image_data:  # Non-trivial message or image
                    await self.context_service.process_conversation_end(
                        self.db, user_id, conversation_id
                    )
                    logger.info(f"Context processing completed for conversation {conversation_id}")
            except Exception as ctx_error:
                # Don't fail the main response if context processing fails
                logger.error(f"Context processing failed for conversation {conversation_id}: {ctx_error}")

            return {
                "message_id": assistant_message.id,
                "conversation_id": conversation_id,
                "response": agent_response["response"],
                "input_tokens": agent_response.get("input_tokens", 0),
                "output_tokens": agent_response.get("output_tokens", 0),
                "timestamp": assistant_message.created_at
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.db.rollback()
            raise

    async def get_user_conversations(self, user_id: int) -> List[Dict]:
        """Get all conversations for a user."""
        try:
            result = await self.db.execute(
                select(ConversationSession)
                .where(ConversationSession.user_id == user_id)
                .order_by(desc(ConversationSession.created_at))
            )
            conversations = result.scalars().all()

            conversation_list = []
            for conv in conversations:
                # Get the last message
                last_message_result = await self.db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.session_id == conv.id)
                    .order_by(desc(ChatMessage.created_at))
                    .limit(1)
                )
                last_message = last_message_result.scalar_one_or_none()

                conversation_list.append({
                    "conversation_id": str(conv.id),  # Use database ID as conversation_id
                    "plant_id": conv.plant_id,
                    "started_at": conv.started_at or conv.created_at,
                    "last_message": last_message.content_text if last_message else None,
                    "last_message_time": last_message.created_at if last_message else conv.created_at,
                    "source": conv.source,
                    "locale": conv.locale
                })

            return conversation_list

        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            raise

    async def get_conversation_messages(
        self,
        user_id: int,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get messages for a specific conversation."""
        try:
            # Convert conversation_id back to int for database lookup
            try:
                conv_id = int(conversation_id)
            except ValueError:
                raise ValueError(f"Invalid conversation_id format: {conversation_id}")

            # First verify the conversation belongs to the user
            conversation = await self._get_conversation(conv_id, user_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            result = await self.db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == conversation.id)
                .order_by(ChatMessage.created_at)
                .offset(offset)
                .limit(limit)
            )
            messages = result.scalars().all()

            return [
                {
                    "message_id": str(msg.id),  # Convert to string for consistency
                    "role": msg.role,
                    "content": msg.content_text,
                    "timestamp": msg.created_at,
                    "model": msg.model,
                    "token_prompt": msg.token_prompt,
                    "token_completion": msg.token_completion,
                    "image_url": msg.image_url
                }
                for msg in messages
            ]

        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            raise

    async def delete_conversation(self, user_id: int, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        try:
            # Convert conversation_id to int for database lookup
            try:
                conv_id = int(conversation_id)
            except ValueError:
                return False

            # First verify the conversation belongs to the user
            conversation = await self._get_conversation(conv_id, user_id)
            if not conversation:
                return False

            # Delete all messages first using delete() method
            from sqlalchemy import delete
            await self.db.execute(
                delete(ChatMessage).where(ChatMessage.session_id == conversation.id)
            )

            # Delete the conversation
            await self.db.delete(conversation)
            await self.db.commit()

            return True

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            await self.db.rollback()
            raise

    async def _get_conversation(self, conversation_id: int, user_id: int) -> Optional[ConversationSession]:
        """Get a conversation by ID and user ID."""
        result = await self.db.execute(
            select(ConversationSession)
            .where(
                and_(
                    ConversationSession.id == conversation_id,
                    ConversationSession.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def _create_conversation(self, user_id: int, plant_id: Optional[int] = None) -> ConversationSession:
        """Create a new conversation session."""
        conversation = ConversationSession(
            user_id=user_id,
            plant_id=plant_id,
            source="chat",
            locale="en",
            started_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def _get_conversation_history(self, conversation_session_id: int, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for context."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == conversation_session_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        messages = result.scalars().all()

        # Return in chronological order (oldest first)
        return [
            {
                "role": msg.role,
                "content": msg.content_text,
                "timestamp": msg.created_at
            }
            for msg in reversed(messages)
        ]

    def _format_context_summary(self, relevant_context: List[Dict]) -> str:
        """Format relevant context entries into a readable summary."""
        if not relevant_context:
            return "No relevant context found"

        # For new context format, just return the most recent summary
        most_recent = relevant_context[0]
        return most_recent.get("summary", "No context available")

    def _extract_plant_info_from_summary(self, summary: str) -> Dict[str, str]:
        """Extract plant information from a context summary."""
        if not summary:
            return {}

        plant_info = {}
        summary_lower = summary.lower()

        # Try to extract plant name - look for common patterns
        # This is a simple heuristic - could be improved with NLP
        plant_keywords = ["fiddle leaf fig", "pothos", "monstera", "snake plant", "succulent",
                         "peace lily", "rubber plant", "philodendron", "spider plant",
                         "aloe", "jade plant", "cactus", "fern"]

        for plant in plant_keywords:
            if plant in summary_lower:
                plant_info["name"] = plant.title()
                break

        # Extract condition/diagnosis information
        if any(word in summary_lower for word in ["yellowing", "yellow leaves", "brown spots"]):
            plant_info["condition"] = "Yellowing/browning leaves"
        elif any(word in summary_lower for word in ["overwater", "root rot"]):
            plant_info["condition"] = "Overwatering issues"
        elif any(word in summary_lower for word in ["underwater", "drooping", "wilting"]):
            plant_info["condition"] = "Underwatering issues"
        elif "diagnosis" in summary_lower or "identified" in summary_lower:
            plant_info["condition"] = "Diagnosed for health issues"

        # Extract diagnosis if available
        if any(word in summary_lower for word in ["overwatering", "root rot"]):
            plant_info["diagnosis"] = "Overwatering and potential root rot"
        elif "underwatering" in summary_lower:
            plant_info["diagnosis"] = "Underwatering stress"
        elif any(word in summary_lower for word in ["pest", "spider mites", "aphids"]):
            plant_info["diagnosis"] = "Pest infestation detected"

        return plant_info
