"""LangGraph state schema for plant assistant conversations."""

from typing import Annotated, List, Optional, Dict, Any
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ConversationState(TypedDict):
    """State schema for LangGraph conversation workflow."""

    # Message history with automatic message reduction
    messages: Annotated[List[BaseMessage], add_messages]

    # User information
    user_id: str
    user_name: Optional[str]

    # Conversation metadata
    conversation_id: Optional[str]
    plant_id: Optional[str]

    # User context from Pinecone
    user_context: Optional[Dict[str, Any]]

    # Tool execution results
    tool_results: Optional[Dict[str, Any]]

    # Image data for plant diagnosis (base64 encoded)
    image_data: Optional[str]

    # Error handling
    error: Optional[str]

    # Token usage tracking
    input_tokens: int
    output_tokens: int
