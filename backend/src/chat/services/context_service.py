"""User context service for conversation summarization and personalization."""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import SecretStr

from src.core.config import settings
from src.conversations.models import ConversationSession, ChatMessage
from src.database import pinecone

logger = logging.getLogger(__name__)


class UserContextService:
    """Service for managing user context through conversation summarization."""

    def __init__(self):
        """Initialize the user context service."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=SecretStr(settings.OPENAI_API_KEY),
            temperature=0.1,
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDINGS_MODEL,
            api_key=SecretStr(settings.OPENAI_EMBEDDINGS_API_KEY),
        )
        self.context_namespace = "user_context"

    async def summarize_conversation(
        self, conversation_id: str, messages: List[BaseMessage]
    ) -> Dict[str, str]:
        """
        Summarize a conversation to extract user context.

        Returns:
            Dict containing summary, plants_discussed, care_preferences, etc.
        """
        try:
            # Convert messages to text format for summarization
            conversation_text = self._format_messages_for_summarization(messages)

            # Create a comprehensive summarization prompt for detailed context
            summary_prompt = f"""
            Analyze this plant care conversation and create a comprehensive summary that will help provide context for future interactions.

            Please provide a detailed summary that includes:
            1. Main topics discussed (plant identification, care issues, recommendations, etc.)
            2. Specific plants mentioned by name or type
            3. User's experience level and preferences mentioned
            4. Problems or concerns raised by the user
            5. Advice given and recommendations made
            6. Any images shared and what they showed (describe plant condition, symptoms, etc.)
            7. Diagnosis provided (if any) and reasoning
            8. User's growing environment (lighting, space, location)
            9. Follow-up questions or ongoing concerns
            10. Whether the conversation involved plant identification, diagnosis, or care advice

            Format as a clear, informative paragraph (3-5 sentences) that captures the key context.
            Focus on information that would be helpful for continuing the conversation or answering follow-up questions.
            If an image was shared, describe what was observed and any diagnosis made.

            Examples:
            - "User asked for beginner-friendly plants suitable for an east-facing apartment with limited space. Recommended pothos, snake plant, and ZZ plant for low maintenance. User expressed interest in plants that can tolerate some neglect and mentioned they travel frequently for work. Discussed watering schedules and light requirements for each recommended plant."

            - "User shared photos of their fiddle leaf fig with yellowing bottom leaves and brown spots. Diagnosed as overwatering issue combined with possible root rot. Recommended reducing watering frequency, checking drainage, and potentially repotting. User mentioned the plant is in a south-facing window and they've been watering twice weekly. Provided care schedule adjustments and next steps for treatment."

            - "User uploaded image of succulent with soft, discolored leaves asking for diagnosis. Identified as root rot from overwatering. Explained signs of healthy vs unhealthy succulent tissue. Provided immediate action plan including removing affected leaves, checking roots, and repotting in well-draining soil. User asked for prevention tips going forward."

            Conversation:
            {conversation_text}

            Provide a comprehensive summary paragraph that includes image analysis and diagnosis details if present:
            """

            response = await self.llm.ainvoke(
                [{"role": "user", "content": summary_prompt}]
            )

            # Extract the summary text
            if hasattr(response, "content") and isinstance(response.content, str):
                summary_text = response.content.strip()
            else:
                summary_text = str(response).strip()

            # Clean up the summary (remove quotes if present)
            summary_text = summary_text.strip('"').strip("'")

            # Create simple context data with the one-sentence summary
            context_data = {
                "summary": summary_text,
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message_count": len(messages),
            }

            logger.info(
                f"Generated comprehensive context summary for conversation {conversation_id}: {summary_text[:100]}..."
            )
            return context_data

        except Exception as e:
            logger.error(f"Error summarizing conversation {conversation_id}: {e}")
            return {
                "summary": "Failed to generate conversation summary",
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    async def store_user_context(
        self, user_id: int, context_data: Dict, conversation_id: str
    ) -> bool:
        """Store or update user context in Pinecone for retrieval."""
        try:
            # Create embedding from context summary
            summary_text = context_data.get("summary", "")
            if not summary_text:
                logger.warning(
                    f"No summary text for user {user_id}, conversation {conversation_id}"
                )
                return False

            embedding = await self.embeddings.aembed_query(summary_text)

            # Use a consistent ID for the same user + conversation combination
            # This ensures updates instead of duplicates for the same conversation
            context_id = f"user_{user_id}_conv_{conversation_id}"

            # Prepare simplified metadata focused on the conversation summary
            metadata = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": context_data.get("timestamp", datetime.utcnow().isoformat()),
                "summary": summary_text,  # Store the full summary text in metadata too
                "message_count": context_data.get("message_count", 0),
                "context_type": "conversation_summary",  # Tag for easy filtering
                "has_images": context_data.get(
                    "has_images", False
                ),  # Whether conversation included images
                "interaction_type": context_data.get(
                    "interaction_type", "general"
                ),  # general, diagnosis, identification, care
                "last_updated": datetime.utcnow().isoformat(),  # Track when this was last updated
            }

            # Check if context already exists for this user + conversation
            try:
                existing_matches = pinecone.query_vector(
                    embedding=[0.0] * 1536,  # Dummy embedding for filter-only query
                    top_k=1,
                    filter={
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "context_type": "conversation_summary"
                    },
                    namespace=self.context_namespace,
                )

                if existing_matches:
                    logger.info(
                        f"Updating existing context for user {user_id}, conversation {conversation_id}"
                    )
                else:
                    logger.info(
                        f"Creating new context entry for user {user_id}, conversation {conversation_id}"
                    )
            except Exception as e:
                logger.warning(f"Could not check for existing context: {e}, proceeding with upsert")

            # Upsert to Pinecone (will update if exists, create if not)
            count = pinecone.upsert_vectors(
                items=[(context_id, embedding, metadata)],
                namespace=self.context_namespace,
            )

            if count > 0:
                logger.info(
                    f"Stored/updated user context for user {user_id}, conversation {conversation_id}"
                )
                return True
            else:
                logger.warning(
                    f"Failed to store/update context in Pinecone for user {user_id}"
                )
                return False

        except Exception as e:
            logger.error(f"Error storing user context for user {user_id}: {e}")
            return False

    async def retrieve_user_context(
        self, user_id: int, current_message: str, top_k: int = 5, conversation_id: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve user context using direct filtering instead of semantic search."""
        try:
            logger.info(f"🔍 CONTEXT SERVICE: Starting retrieval for user {user_id}")
            if conversation_id:
                logger.info(f"  Filtering for specific conversation: {conversation_id}")
            logger.info(f"  Namespace: {self.context_namespace}")
            logger.info(f"  Requested top_k: {top_k}")

            # Create filter for user_id and optionally conversation_id
            query_filter: Dict[str, Any] = {"user_id": user_id}
            if conversation_id:
                query_filter["conversation_id"] = conversation_id

            logger.info(f"  Filter: {query_filter}")

            # Use a dummy embedding since we're only using filters
            # This is more efficient than creating an actual embedding for semantic search
            dummy_embedding = [0.0] * 1536  # Standard OpenAI embedding dimension

            logger.info("  Querying Pinecone with filter-only approach...")
            matches = pinecone.query_vector(
                embedding=dummy_embedding,
                top_k=top_k,
                filter=query_filter,
                namespace=self.context_namespace,
            )

            logger.info(f"  Pinecone returned {len(matches)} raw matches")

            # Log all matches with their metadata
            for i, match in enumerate(matches):
                score = getattr(match, "score", 0)
                match_id = getattr(match, "id", "unknown")
                metadata = getattr(match, "metadata", {})
                conv_id = metadata.get("conversation_id", "N/A")
                timestamp = metadata.get("timestamp", "N/A")
                logger.info(
                    f"    Match {i + 1}: ID={match_id}, Conversation={conv_id}, Timestamp={timestamp}"
                )

            # Format results - return all results without threshold filtering
            context_results = []
            logger.info("  Processing all context results without threshold filtering")

            for match in matches:
                metadata = getattr(match, "metadata", {})
                # For filter-based queries, we don't have meaningful relevance scores
                # Use timestamp-based relevance instead (more recent = more relevant)
                timestamp_str = metadata.get("timestamp", "")
                try:
                    # Calculate recency score (more recent = higher score)
                    if timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        days_ago = (datetime.now().replace(tzinfo=timestamp.tzinfo) - timestamp).days
                        # Score decreases with age: 1.0 for today, 0.9 for 1 day ago, etc.
                        recency_score = max(0.1, 1.0 - (days_ago * 0.1))
                    else:
                        recency_score = 0.5  # Default score for missing timestamp
                except Exception:
                    recency_score = 0.5

                context_results.append(
                    {
                        "relevance_score": recency_score,
                        "conversation_id": metadata.get("conversation_id"),
                        "timestamp": metadata.get("timestamp"),
                        "summary": metadata.get("summary", ""),  # The key context information
                        "message_count": metadata.get("message_count", 0),
                        "context_type": metadata.get("context_type", "conversation_summary"),
                        "user_id": metadata.get("user_id"),  # Add for debugging
                        "has_images": metadata.get("has_images", False),
                        "interaction_type": metadata.get("interaction_type", "general"),
                        "last_updated": metadata.get("last_updated", ""),
                    }
                )
                logger.info(f"    ✅ Match included: Recency Score={recency_score:.3f}")

            # Sort by recency score (most recent first)
            context_results.sort(key=lambda x: x["relevance_score"], reverse=True)

            logger.info(
                f"Retrieved {len(context_results)} context entries for user {user_id} using filter-based approach"
            )
            return context_results

        except Exception as e:
            logger.error(f"Error retrieving user context for user {user_id}: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def process_conversation_end(
        self, db: AsyncSession, user_id: int, conversation_id: str
    ) -> bool:
        """Process conversation when it ends to generate and store context."""
        try:
            # Since we don't have conversation_id in the database, we need to work with sessions
            # This is a simplified version that processes recent messages for the user
            result = await db.execute(
                select(ChatMessage)
                .join(ConversationSession)
                .where(ConversationSession.user_id == user_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(20)  # Get recent messages for context
            )
            messages = result.scalars().all()

            if len(messages) < 2:  # Need at least user message and assistant response
                logger.info(
                    f"Too few messages in conversation {conversation_id}, skipping summarization"
                )
                return True

            # Convert to BaseMessage format with image information
            base_messages = []
            for msg in messages:
                message_content = msg.content_text

                # Add image indicator if image was shared
                if msg.image_url:
                    message_content += (
                        " [IMAGE SHARED: Plant photo uploaded for analysis]"
                    )

                base_messages.append(
                    {
                        "role": msg.role,
                        "content": message_content,
                        "timestamp": msg.created_at,
                        "has_image": bool(msg.image_url),
                    }
                )

            # Generate context summary
            context_data = await self.summarize_conversation(
                conversation_id, base_messages
            )

            # Store in Pinecone
            return await self.store_user_context(user_id, context_data, conversation_id)

        except Exception as e:
            logger.error(
                f"Error processing conversation end for {conversation_id}: {e}"
            )
            return False

    async def get_user_context_summary(self, user_id: int) -> Dict:
        """Get a high-level summary of user's context across all conversations."""
        try:
            # Query recent context entries for this user
            dummy_embedding = [0.0] * 1536  # Dummy embedding for filter-only query
            matches = pinecone.query_vector(
                embedding=dummy_embedding,
                top_k=20,
                filter={"user_id": user_id},
                namespace=self.context_namespace,
            )

            if not matches:
                return {"message": "No context found for user"}

            # Collect conversation summaries
            conversation_summaries = []
            conversation_count = 0

            for match in matches:
                metadata = getattr(match, "metadata", {})
                if metadata.get("context_type") == "conversation_summary":
                    conversation_count += 1
                    summary_info = {
                        "conversation_id": metadata.get("conversation_id"),
                        "timestamp": metadata.get("timestamp"),
                        "summary": metadata.get("summary", ""),
                        "message_count": metadata.get("message_count", 0),
                    }
                    conversation_summaries.append(summary_info)

            return {
                "user_id": user_id,
                "total_conversations": conversation_count,
                "conversation_summaries": conversation_summaries[
                    :10
                ],  # Return last 10 summaries
                "last_updated": datetime.utcnow().isoformat(),
                "context_type": "user_conversation_history",
            }

        except Exception as e:
            logger.error(f"Error getting user context summary for user {user_id}: {e}")
            return {"error": str(e)}

    def _format_messages_for_summarization(self, messages: List[BaseMessage]) -> str:
        """Format messages for summarization prompt."""
        formatted = []
        for msg in messages:
            # Handle dictionary format (from database queries)
            if isinstance(msg, dict):
                role = msg.get("role", "UNKNOWN").upper()
                content = msg.get("content", str(msg))
                timestamp = msg.get("timestamp", "")

                # Add timestamp info if available
                if timestamp:
                    formatted.append(f"{role} ({timestamp}): {content}")
                else:
                    formatted.append(f"{role}: {content}")

            # Handle BaseMessage objects
            elif hasattr(msg, "type"):
                role = msg.type.upper()
                content = str(msg.content) if hasattr(msg, "content") else str(msg)
                formatted.append(f"{role}: {content}")

            # Fallback for other formats
            else:
                role = "UNKNOWN"
                content = str(msg)
                formatted.append(f"{role}: {content}")

        return "\n\n".join(formatted)
