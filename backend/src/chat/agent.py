"""LangGraph workflow for plant assistant chatbot."""

import logging
from typing import Dict, Any, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from pydantic import SecretStr

from src.core.config import settings
from .state import ConversationState

logger = logging.getLogger(__name__)


class PlantAssistantAgent:
    """LangGraph-powered plant assistant agent with diagnosis tool integration."""

    def __init__(self):
        """Initialize the agent with OpenAI LLM and plant tools."""
        # Import tools and services here to avoid circular import
        from .tools import PLANT_TOOLS
        from .services.context_service import UserContextService

        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=SecretStr(settings.OPENAI_API_KEY),
            base_url=settings.OPENAI_BASE_URL,
        )

        # Initialize user context service
        self.context_service = UserContextService()

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(PLANT_TOOLS)

        # Create tool node for tool execution
        self.tool_node = ToolNode(PLANT_TOOLS)

        # Build the conversation graph
        self.graph = self._build_graph()

        # Compile the graph with memory
        self.app = self.graph.compile(checkpointer=MemorySaver())

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph conversation workflow."""
        # Create the state graph
        workflow = StateGraph(ConversationState)

        # Add nodes
        workflow.add_node("load_context", self._load_user_context)
        workflow.add_node("retrieve_context", self._retrieve_relevant_context)
        workflow.add_node("chat", self._chat_with_tools)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("save_context", self._save_user_context)

        # Set entry point
        workflow.add_edge(START, "load_context")

        # Context loading flows to context retrieval
        workflow.add_edge("load_context", "retrieve_context")

        # Context retrieval flows to chat
        workflow.add_edge("retrieve_context", "chat")

        # Conditional edge from chat: if tools called, go to tools, otherwise save context
        workflow.add_conditional_edges(
            "chat", self._should_use_tools, {"tools": "tools", "save": "save_context"}
        )

        # After tool execution, go back to chat for response
        workflow.add_edge("tools", "chat")

        # End after saving context
        workflow.add_edge("save_context", END)

        return workflow

    async def _load_user_context(self, state: ConversationState) -> ConversationState:
        """Load user context from Pinecone for personalization."""
        try:
            # First check if context was already provided from the chat service
            if state.get("user_context") and isinstance(state["user_context"], dict):
                # Context already provided, just validate and use it
                logger.info(f"Using pre-loaded context for user {state.get('user_id')}")
                return state

            user_id = state.get("user_id")
            current_message = ""

            # Get the latest user message for context matching
            human_messages = [
                msg for msg in state["messages"] if isinstance(msg, HumanMessage)
            ]
            if human_messages:
                current_message = human_messages[-1].content

            if (
                user_id
                and current_message
                and isinstance(user_id, int)
                and isinstance(current_message, str)
            ):
                # Use UserContextService to retrieve relevant context
                context_data = await self.context_service.retrieve_user_context(
                    user_id=user_id,
                    current_message=current_message,
                    top_k=3,
                    conversation_id=state.get("conversation_id")  # Pass conversation_id for filtering
                )

                if context_data:
                    user_context = {
                        "user_id": user_id,
                        "plants_discussed": [],
                        "experience_level": "beginner",
                        "preferences": "",
                        "common_issues": "",
                        "environment": "",
                        "goals": "",
                    }

                    # Aggregate context from multiple entries
                    for ctx in context_data:
                        if ctx.get("plants_discussed"):
                            user_context["plants_discussed"].extend(
                                ctx["plants_discussed"]
                            )
                        if ctx.get("experience_level"):
                            user_context["experience_level"] = ctx["experience_level"]
                        if ctx.get("preferences"):
                            user_context["preferences"] = ctx["preferences"]
                        if ctx.get("common_issues"):
                            user_context["common_issues"] = ctx["common_issues"]
                        if ctx.get("environment"):
                            user_context["environment"] = ctx["environment"]
                        if ctx.get("goals"):
                            user_context["goals"] = ctx["goals"]

                    # Remove duplicates from plants list
                    user_context["plants_discussed"] = list(
                        set(user_context["plants_discussed"])
                    )

                else:
                    # Default context for new users
                    user_context = {
                        "user_id": user_id,
                        "plants_discussed": [],
                        "experience_level": "beginner",
                        "preferences": "",
                        "common_issues": "",
                        "environment": "",
                        "goals": "",
                    }
            else:
                # Fallback context
                user_context = {
                    "user_id": user_id,
                    "plants_discussed": [],
                    "experience_level": "beginner",
                }

            state["user_context"] = user_context
            logger.info(f"Loaded context for user {user_id}")

        except Exception as e:
            logger.error(f"Error loading user context: {e}")
            state["user_context"] = {
                "user_id": state.get("user_id"),
                "experience_level": "beginner",
            }

        return state

    async def _retrieve_relevant_context(
        self, state: ConversationState
    ) -> ConversationState:
        """Retrieve relevant context from Pinecone for the current conversation."""
        try:
            user_id = state.get("user_id")
            messages = state["messages"]

            # Get the latest user message for context matching
            human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]

            if not human_messages:
                logger.info("No user messages found for context retrieval")
                return state

            current_message = human_messages[-1].content

            # Extract just text content if it's a complex message structure
            if isinstance(current_message, list):
                text_parts = [
                    part.get("text", "")
                    for part in current_message
                    if isinstance(part, dict) and "text" in part
                ]
                current_message = " ".join(text_parts)
            elif not isinstance(current_message, str):
                current_message = str(current_message)

            logger.info(f"Retrieving context for message: {current_message[:100]}...")

            if user_id and current_message:
                # Convert user_id to int if it's a string
                user_id_int = None
                try:
                    user_id_int = int(user_id) if isinstance(user_id, str) else user_id
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert user_id to int: {user_id}")
                    return state

                logger.info("🔍 STARTING CONTEXT RETRIEVAL:")
                logger.info(f"  User ID: {user_id_int}")
                logger.info(f"  Query: '{current_message[:200]}'")
                logger.info("  Requesting top_k: 5 results")

                # Retrieve relevant context using the context service
                context_results = await self.context_service.retrieve_user_context(
                    user_id=user_id_int,
                    current_message=current_message,
                    top_k=5,  # Get more context for better decision making
                    conversation_id=state.get("conversation_id"),  # Pass conversation_id for filtering
                )

                logger.info("📊 CONTEXT RETRIEVAL COMPLETE:")
                logger.info(
                    f"  Total results returned: {len(context_results) if context_results else 0}"
                )

                if context_results:
                    # Log all context results first
                    logger.info(f"🔍 RETRIEVED {len(context_results)} CONTEXT RESULTS:")
                    for i, ctx in enumerate(context_results):
                        relevance = ctx.get("relevance_score", 0)
                        summary = (
                            ctx.get("summary", "")[:150] + "..."
                            if len(ctx.get("summary", "")) > 150
                            else ctx.get("summary", "")
                        )
                        user_context_id = ctx.get("user_id", "N/A")
                        timestamp = ctx.get("timestamp", "N/A")
                        logger.info(
                            f"  Context {i + 1}: [Relevance: {relevance:.3f}] [User: {user_context_id}] [Time: {timestamp}] {summary}"
                        )

                    # Create a context summary for the LLM
                    context_summaries = []
                    for ctx in context_results:
                        relevance = ctx.get("relevance_score", 0)
                        summary = ctx.get("summary", "")
                        if summary:  # Include all context with summaries (no threshold filtering)
                            context_summaries.append(
                                f"[Relevance: {relevance:.2f}] {summary}"
                            )

                    if context_summaries:
                        # Add context information to the conversation
                        context_message = f"""🌱 IMPORTANT: RETRIEVED CONTEXT FROM PREVIOUS CONVERSATIONS 🌱

The following context contains information from your previous plant care discussions:

{chr(10).join(context_summaries[:3])}

⚠️ CRITICAL: Use this context to inform your response. If this context contains recent information about the same plant the user is asking about, provide a direct response that references and builds upon this previous discussion. Only use diagnosis tools if you need NEW information not already available in this context.

If the user is asking a follow-up question about a plant mentioned in the context above, acknowledge the previous conversation and provide continuity."""

                        # Insert context message before the user's message for the LLM to see
                        if len(messages) >= 1:
                            # Insert context right before the latest user message
                            context_msg = SystemMessage(content=context_message)
                            messages.insert(-1, context_msg)
                            state["messages"] = messages

                        logger.info(
                            f"📝 CONTEXT INJECTED INTO LLM: Added {len(context_summaries)} context entries without threshold filtering"
                        )
                        logger.info(
                            f"📋 CONTEXT MESSAGE CONTENT: {context_message[:300]}..."
                        )
                    else:
                        logger.info(
                            "❌ No context found with summary content"
                        )
                else:
                    logger.warning("⚠️  NO CONTEXT RESULTS FOUND:")
                    logger.warning("  This could mean:")
                    logger.warning(
                        "  1. No previous conversations stored in Pinecone for this user"
                    )
                    logger.warning("  2. Semantic search found no relevant matches")
                    logger.warning("  3. Pinecone connection/query issue")
                    logger.warning("  4. Context service configuration problem")
            else:
                logger.warning("❌ CONTEXT RETRIEVAL SKIPPED:")
                logger.warning(
                    f"  Missing requirements - user_id: {user_id}, current_message length: {len(current_message) if current_message else 0}"
                )

        except Exception as e:
            logger.error(f"Error retrieving relevant context: {e}")
            # Don't fail the workflow if context retrieval fails

        return state

    async def _chat_with_tools(self, state: ConversationState) -> ConversationState:
        """Main chat node that can call tools."""
        try:
            messages = state["messages"]
            user_context = state.get("user_context", {})

            # Check if this is a second pass after tool execution
            tool_messages = [msg for msg in messages if hasattr(msg, "tool_call_id")]
            if tool_messages:
                logger.info(
                    f"🔄 SECOND PASS AFTER TOOL EXECUTION - Found {len(tool_messages)} tool response messages"
                )
                for i, tool_msg in enumerate(tool_messages):
                    if hasattr(tool_msg, "content"):
                        content_preview = (
                            str(tool_msg.content)[:200] + "..."
                            if len(str(tool_msg.content)) > 200
                            else str(tool_msg.content)
                        )
                        logger.info(f"  Tool Response {i + 1}: {content_preview}")

            # Set the current state in tools so they can access image data
            from .tools import set_current_state

            set_current_state(state)

            # Add system message with user context if not present
            if not any(isinstance(msg, SystemMessage) for msg in messages):
                system_prompt = self._create_system_prompt(user_context or {})
                messages = [SystemMessage(content=system_prompt)] + messages

            # Always use the LLM with tools - let it decide when to call diagnosis tool
            response = await self.llm_with_tools.ainvoke(messages)

            # Log what the LLM received and decided
            logger.info("🤖 LLM DECISION SUMMARY:")
            logger.info(f"  Total messages sent to LLM: {len(messages)}")

            # Count different message types
            system_msgs = [msg for msg in messages if isinstance(msg, SystemMessage)]
            human_msgs = [msg for msg in messages if isinstance(msg, HumanMessage)]
            logger.info(f"  - System messages: {len(system_msgs)}")
            logger.info(f"  - Human messages: {len(human_msgs)}")

            # Check if LLM decided to call tools
            tool_calls = getattr(response, "tool_calls", None)
            if tool_calls:
                logger.info(f"🔧 LLM DECIDED TO CALL {len(tool_calls)} TOOL(S):")
                for i, tool_call in enumerate(tool_calls):
                    tool_name = tool_call.get("name", "unknown")
                    tool_args = tool_call.get("args", {})
                    logger.info(
                        f"  Tool {i + 1}: {tool_name} with args: {list(tool_args.keys())}"
                    )
            else:
                logger.info("💭 LLM DECIDED NOT TO CALL ANY TOOLS - Direct response")

            state["messages"] = messages + [response]
            logger.info(f"LLM response generated for user {state.get('user_id')}")

        except Exception as e:
            logger.error(f"Error in chat node: {e}")
            state["error"] = str(e)
            # Add error message
            error_msg = AIMessage(
                content="I apologize, but I encountered an error. Please try again."
            )
            state["messages"] = state["messages"] + [error_msg]

        return state

    def _should_use_tools(self, state: ConversationState) -> str:
        """Determine if tools should be called based on the last message."""
        messages = state["messages"]
        if not messages:
            return "save"

        last_message = messages[-1]

        # Check if the last message has tool calls
        # Use getattr to safely check for tool_calls attribute
        tool_calls = getattr(last_message, "tool_calls", None)
        if tool_calls:
            return "tools"

        return "save"

    async def _save_user_context(self, state: ConversationState) -> ConversationState:
        """Save/update user context to Pinecone."""
        try:
            # TODO: Implement Pinecone user context saving
            # Extract new context from conversation and update user profile

            logger.info(f"Context saved for user {state.get('user_id')}")

        except Exception as e:
            logger.error(f"Error saving user context: {e}")

        return state

    def _create_system_prompt(self, user_context: Dict[str, Any]) -> str:
        """Create a personalized system prompt based on user context."""
        user_name = user_context.get("name", "there")
        experience = user_context.get("experience_level", "beginner")

        # Include context about recently discussed plants
        plant_context = ""
        most_recent_plant = user_context.get("most_recent_plant")
        plants_discussed = user_context.get("plants_discussed", [])

        if most_recent_plant:
            plant_name = most_recent_plant.get("name", "Unknown plant")
            condition = most_recent_plant.get("condition", "Unknown condition")
            diagnosis = most_recent_plant.get("diagnosis", "")

            plant_context = f"""
RECENT PLANT CONTEXT:
- You recently analyzed a {plant_name}
- Current condition: {condition}
- Diagnosis: {diagnosis}
- When the user asks follow-up questions about "the plant", "it", or "my plant", they're referring to this {plant_name}
"""
        elif plants_discussed:
            plant_names = [p.get("name", "Unknown") for p in plants_discussed[:2]]
            plant_context = f"""
RECENT PLANT CONTEXT:
- Recently discussed plants: {", ".join(plant_names)}
- When the user refers to "the plant" or "my plant", they likely mean one of these
"""

        base_prompt = f"""You are a helpful plant care assistant chatting with {user_name}, who has {experience} level experience with plants.

{plant_context}

**CONTEXT-FIRST DECISION MAKING:**
Before making any decisions or using tools, ALWAYS review any "RETRIEVED CONTEXT" messages in the conversation. This context contains relevant information from previous conversations and plant care cases that should inform your responses and tool usage.

You have access to two specialized plant analysis tools:

1. **diagnose_plant_from_image** - Use ONLY when user has uploaded a plant image
   - Performs visual AI analysis of plant photos
   - Identifies species and assesses health from visual symptoms
   - Requires image data to function properly

2. **diagnose_plant_from_text** - Use when user describes plants/symptoms in text WITHOUT uploading an image
   - Searches our comprehensive knowledge database
   - Provides expert advice based on similar cases
   - Works with text descriptions of plants and symptoms

**CONTEXT-INFORMED TOOL SELECTION RULES:**
- **First, check retrieved context** for relevant plant information from previous discussions
- **If context contains sufficient information** to answer the user's question, you can provide a direct response based on that context
- **User uploaded image** → Use `diagnose_plant_from_image` (unless context already contains recent analysis of the same plant)
- **User describes plant/symptoms in text only** → Use `diagnose_plant_from_text` (unless context already has relevant information)
- **If context shows previous plant discussion** → Reference that context and provide updates or follow-up advice directly
- **NEVER use both tools for the same question**
- **Use tools when context is insufficient** or when user is asking about a new plant/issue

**WHEN TO USE TOOLS vs WHEN TO USE CONTEXT:**
- **Use Context Directly**: When retrieved context contains recent information about the same plant/issue the user is asking about
- **Use `diagnose_plant_from_image`**: For new plant images or when user wants fresh analysis
- **Use `diagnose_plant_from_text`**: For new plant care questions without sufficient context
- **Follow-up questions**: Use context first, then tools if needed for new information

**Key guidelines for responses:**
- **FIRST: Review any RETRIEVED CONTEXT messages for relevant information**
- **If context is sufficient**, provide a direct response that references and builds upon the context
- **If context is insufficient**, use the appropriate diagnosis tool
- **Integrate retrieved context** with tool results when both are used
- When retrieved context mentions the same plant the user is asking about, reference it directly
- For follow-up questions about "the plant", "it", or "my plant", prioritize using context over tools
- Be direct and acknowledge previous discussions when context is available
- When context contains a recent diagnosis, provide follow-up advice or updates based on that information

Examples of context-informed responses:
- Context shows previous tomato plant discussion + Question: "How is my plant doing?" → "Based on our recent discussion about your tomato plant's internal rot issue, I hope the treatment is working well. How are the fruits looking now? Are you seeing any improvement since we discussed improving drainage and reducing watering?"
- Context shows Monstera diagnosis + Question: "Is my plant healthy?" → "Looking at our previous discussion about your Monstera's overwatering issues, how has the plant responded to the care adjustments we discussed? Are the leaves still showing yellowing, or have you seen improvement?"
- Context shows multiple plants + Question: "What's wrong with the leaves?" → Use context to determine which plant, then provide targeted advice or use appropriate tool for new analysis
- New question without relevant context → Use appropriate tool, but acknowledge any general context if relevant

Remember: PRIORITIZE retrieved context for follow-up questions and ongoing plant care discussions. Use tools when context is insufficient or when analyzing new plants/images. Always acknowledge previous conversations and build upon them for a personalized experience."""

        return base_prompt

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        user_name: Optional[str] = None,
        plant_id: Optional[str] = None,
        image_data: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a user message through the LangGraph workflow."""

        # If image data is provided, automatically trigger diagnosis
        if image_data:
            # Extract just the base64 data (remove data URL prefix if present)
            if "," in image_data:
                image_base64 = image_data.split(",")[1]
            else:
                image_base64 = image_data

            # Modify message to indicate image analysis is needed
            message_with_context = f"{message}\n\n[IMAGE PROVIDED - Please analyze this plant image using the diagnosis tool]"

            # Store image data in the initial state for tool use
            initial_state = ConversationState(
                messages=[HumanMessage(content=message_with_context)],
                user_id=user_id,
                user_name=user_name,
                conversation_id=conversation_id,
                plant_id=plant_id,
                user_context=user_context,  # Pass user context
                tool_results=None,
                image_data=image_base64,  # Store image data for tool access
                error=None,
                input_tokens=0,
                output_tokens=0,
            )
        else:
            # Create initial state without image
            initial_state = ConversationState(
                messages=[HumanMessage(content=message)],
                user_id=user_id,
                user_name=user_name,
                conversation_id=conversation_id,
                plant_id=plant_id,
                user_context=user_context,  # Pass user context
                tool_results=None,
                image_data=None,
                error=None,
                input_tokens=0,
                output_tokens=0,
            )

        # Create config for conversation threading
        config = RunnableConfig(
            configurable={"thread_id": conversation_id or f"user_{user_id}"}
        )

        try:
            # Run the workflow
            final_state = await self.app.ainvoke(initial_state, config=config)

            # Extract the final AI response
            messages = final_state["messages"]
            ai_response = None

            # Find the last AI message
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    ai_response = msg.content
                    break

            return {
                "response": ai_response
                or "I apologize, but I couldn't generate a proper response.",
                "conversation_id": final_state.get("conversation_id"),
                "input_tokens": final_state.get("input_tokens", 0),
                "output_tokens": final_state.get("output_tokens", 0),
                "error": final_state.get("error"),
                "tool_results": final_state.get("tool_results"),
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your message. Please try again.",
                "error": str(e),
                "input_tokens": 0,
                "output_tokens": 0,
            }
