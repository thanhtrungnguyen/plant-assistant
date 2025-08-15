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
from .tools import PLANT_TOOLS
from .services.context_service import UserContextService

logger = logging.getLogger(__name__)


class PlantAssistantAgent:
    """LangGraph-powered plant assistant agent with diagnosis tool integration."""

    def __init__(self):
        """Initialize the agent with OpenAI LLM and plant tools."""
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
        workflow.add_node("chat", self._chat_with_tools)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("save_context", self._save_user_context)

        # Set entry point
        workflow.add_edge(START, "load_context")

        # Context loading flows to chat
        workflow.add_edge("load_context", "chat")

        # Conditional edge from chat: if tools called, go to tools, otherwise save context
        workflow.add_conditional_edges(
            "chat",
            self._should_use_tools,
            {
                "tools": "tools",
                "save": "save_context"
            }
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
            human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
            if human_messages:
                current_message = human_messages[-1].content

            if user_id and current_message and isinstance(user_id, int) and isinstance(current_message, str):
                # Use UserContextService to retrieve relevant context
                context_data = await self.context_service.retrieve_user_context(
                    user_id=user_id,
                    current_message=current_message,
                    top_k=3
                )

                if context_data:
                    user_context = {
                        "user_id": user_id,
                        "plants_discussed": [],
                        "experience_level": "beginner",
                        "preferences": "",
                        "common_issues": "",
                        "environment": "",
                        "goals": ""
                    }

                    # Aggregate context from multiple entries
                    for ctx in context_data:
                        if ctx.get("plants_discussed"):
                            user_context["plants_discussed"].extend(ctx["plants_discussed"])
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
                    user_context["plants_discussed"] = list(set(user_context["plants_discussed"]))

                else:
                    # Default context for new users
                    user_context = {
                        "user_id": user_id,
                        "plants_discussed": [],
                        "experience_level": "beginner",
                        "preferences": "",
                        "common_issues": "",
                        "environment": "",
                        "goals": ""
                    }
            else:
                # Fallback context
                user_context = {
                    "user_id": user_id,
                    "plants_discussed": [],
                    "experience_level": "beginner"
                }

            state["user_context"] = user_context
            logger.info(f"Loaded context for user {user_id}")

        except Exception as e:
            logger.error(f"Error loading user context: {e}")
            state["user_context"] = {"user_id": state.get("user_id"), "experience_level": "beginner"}

        return state

    async def _chat_with_tools(self, state: ConversationState) -> ConversationState:
        """Main chat node that can call tools."""
        try:
            messages = state["messages"]
            user_context = state.get("user_context", {})
            image_data = state.get("image_data")

            # Add system message with user context if not present
            if not any(isinstance(msg, SystemMessage) for msg in messages):
                system_prompt = self._create_system_prompt(user_context or {})
                messages = [SystemMessage(content=system_prompt)] + messages

            # If we have image data and this is the first time processing the message,
            # automatically call the diagnosis tool
            if image_data and len(messages) <= 2:  # System message + user message
                from .tools import diagnose_plant_health

                logger.info("Image data detected, automatically calling diagnosis tool")

                # Call the diagnosis tool directly
                diagnosis_result = await diagnose_plant_health.ainvoke({
                    "image_data": image_data,
                    "user_notes": "User provided an image for analysis"
                })

                # Parse the diagnosis result
                import json
                try:
                    diagnosis_data = json.loads(diagnosis_result)

                    # Create a more direct response based on the user's original message
                    user_message_content = ""
                    if messages:
                        last_msg = messages[-1]
                        if hasattr(last_msg, 'content'):
                            if isinstance(last_msg.content, str):
                                user_message_content = last_msg.content
                            elif isinstance(last_msg.content, list) and len(last_msg.content) > 0:
                                # Handle list content (like multi-part messages)
                                text_parts = [part for part in last_msg.content if isinstance(part, str)]
                                user_message_content = " ".join(text_parts) if text_parts else ""

                    if diagnosis_data.get("success"):
                        plant_name = diagnosis_data.get("plant_identification", {}).get("plant_name", "Unknown plant")
                        condition = diagnosis_data.get("health_assessment", {}).get("condition", "Unknown condition")
                        diagnosis = diagnosis_data.get("health_assessment", {}).get("diagnosis", "")

                        # Generate direct response based on what the user asked
                        if "what plant" in user_message_content.lower() or "identify" in user_message_content.lower():
                            # For plant identification questions
                            if plant_name != "Unknown plant":
                                direct_response = f"This is a {plant_name}."
                            else:
                                direct_response = "I couldn't identify the specific plant species from this image. Could you provide a clearer photo?"

                        elif "healthy" in user_message_content.lower() or "wrong" in user_message_content.lower() or "problem" in user_message_content.lower():
                            # For health assessment questions
                            if condition != "Unknown condition" and diagnosis:
                                direct_response = f"Your {plant_name} shows signs of {condition.lower()}. {diagnosis}"
                                recommendations = diagnosis_data.get("treatment_recommendations", [])
                                if recommendations and len(recommendations) > 0:
                                    if isinstance(recommendations[0], dict) and "action" in recommendations[0]:
                                        main_treatment = recommendations[0]["action"]
                                    else:
                                        main_treatment = str(recommendations[0])
                                    direct_response += f" Recommended action: {main_treatment}"
                            else:
                                direct_response = f"I can see this is a {plant_name}, but I need a clearer image to assess its health properly."
                        else:
                            # General response
                            if plant_name != "Unknown plant":
                                if condition and condition.lower() != "unknown condition":
                                    direct_response = f"I can see this is a {plant_name}. The plant's condition appears to be {condition.lower()}."
                                    if diagnosis:
                                        direct_response += f" {diagnosis}"
                                else:
                                    direct_response = f"I can see this is a {plant_name}. The plant looks generally healthy."
                            else:
                                direct_response = "I'm having trouble identifying this plant from the image. Could you provide a clearer photo or tell me more about it?"

                        # Store diagnosis in tool results AND user context for future reference
                        state["tool_results"] = diagnosis_data

                        # Update user context with the diagnosed plant information
                        current_context = state.get("user_context", {}) or {}
                        if plant_name != "Unknown plant":
                            # Add the plant to recently discussed plants
                            plants_discussed = current_context.get("plants_discussed", [])
                            plant_info = {
                                "name": plant_name,
                                "condition": condition,
                                "diagnosis": diagnosis,
                                "timestamp": "recent",
                                "conversation_id": state.get("conversation_id")
                            }

                            # Add to beginning of list (most recent first) and limit to 3 recent plants
                            plants_discussed.insert(0, plant_info)
                            current_context["plants_discussed"] = plants_discussed[:3]
                            current_context["most_recent_plant"] = plant_info

                            state["user_context"] = current_context

                        # Create AI response directly
                        ai_response = AIMessage(content=direct_response)
                        state["messages"] = messages + [ai_response]

                        logger.info(f"Generated direct response from diagnosis: {direct_response[:100]}...")
                        return state
                    else:
                        # Handle error case
                        error_msg = diagnosis_data.get("message", "I couldn't analyze the image properly. Please try with a clearer photo.")
                        ai_response = AIMessage(content=error_msg)
                        state["messages"] = messages + [ai_response]
                        return state

                except json.JSONDecodeError:
                    logger.error("Failed to parse diagnosis result JSON")
                    error_msg = AIMessage(content="I had trouble analyzing the image. Please try again with a clearer photo.")
                    state["messages"] = messages + [error_msg]
                    return state
            else:
                # Normal LLM processing without image
                response = await self.llm_with_tools.ainvoke(messages)
                state["messages"] = messages + [response]

            logger.info(f"LLM response generated for user {state.get('user_id')}")

        except Exception as e:
            logger.error(f"Error in chat node: {e}")
            state["error"] = str(e)
            # Add error message
            error_msg = AIMessage(content="I apologize, but I encountered an error. Please try again.")
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
        tool_calls = getattr(last_message, 'tool_calls', None)
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
- Recently discussed plants: {', '.join(plant_names)}
- When the user refers to "the plant" or "my plant", they likely mean one of these
"""

        base_prompt = f"""You are a helpful plant care assistant chatting with {user_name}, who has {experience} level experience with plants.

{plant_context}

You have access to a plant diagnosis tool that can analyze plant images for health issues, diseases, pests, and plant identification. When a user shares a plant image, ALWAYS use the diagnose_plant_health tool to analyze it.

Key guidelines for responses:
- Be direct and concise in your answers
- When asked for specific information (plant name, diagnosis, care tips), provide it directly without long explanations
- If asked "What plant is this?", respond with just the plant name from the diagnosis
- If asked about plant health, give a direct assessment based on the diagnosis
- Use the diagnosis tool results to provide specific, actionable advice
- Keep responses conversational but focused
- For plant identification: Just state the plant name and maybe one key characteristic
- For health issues: State the problem and the main solution
- When users ask follow-up questions about "the plant", "it", or "my plant" without context, refer to the most recent plant discussed
- Ask follow-up questions only when you need more information for diagnosis

Examples of direct responses:
- Question: "What plant is this?" → Answer: "This is a Monstera Deliciosa."
- Question: "Is my plant healthy?" → Answer: "Your plant has overwatering issues. Reduce watering frequency to once per week."
- Question: "What's wrong with the leaves?" → Answer: "The yellowing leaves indicate nutrient deficiency. Use a balanced fertilizer monthly."
- Question: "How often should I water it?" (after plant diagnosis) → Answer: "Water your [plant name] once a week, allowing soil to dry between waterings."

Remember: Use the diagnosis tool for any plant image, then give direct, helpful responses based on the results. For follow-up questions, reference the recent plant context."""

        return base_prompt

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        user_name: Optional[str] = None,
        plant_id: Optional[str] = None,
        image_data: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
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
                output_tokens=0
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
                output_tokens=0
            )

        # Create config for conversation threading
        config = RunnableConfig(
            configurable={
                "thread_id": conversation_id or f"user_{user_id}"
            }
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
                "response": ai_response or "I apologize, but I couldn't generate a proper response.",
                "conversation_id": final_state.get("conversation_id"),
                "input_tokens": final_state.get("input_tokens", 0),
                "output_tokens": final_state.get("output_tokens", 0),
                "error": final_state.get("error"),
                "tool_results": final_state.get("tool_results")
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your message. Please try again.",
                "error": str(e),
                "input_tokens": 0,
                "output_tokens": 0
            }
