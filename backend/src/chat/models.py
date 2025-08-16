"""Chat models - aliases for conversation models."""

# Import and alias the existing conversation models
from src.conversations.models import (
    ConversationSession as BaseConversationSession,
    ChatMessage as BaseChatMessage,
)


# Create aliases with adjusted field names for compatibility
class ConversationSession(BaseConversationSession):
    """ConversationSession with conversation_id field for compatibility."""

    @property
    def conversation_id(self) -> str:
        """Use ID as conversation_id for compatibility."""
        return str(self.id)


class ChatMessage(BaseChatMessage):
    """ChatMessage with adjusted field names for compatibility."""

    @property
    def conversation_session_id(self) -> int:
        """Alias for session_id."""
        return self.session_id

    @property
    def content(self) -> str:
        """Alias for content_text."""
        return self.content_text

    @content.setter
    def content(self, value: str):
        """Setter for content."""
        self.content_text = value
