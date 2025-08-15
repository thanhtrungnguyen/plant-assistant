"""LangChain-based chat service for advanced conversation handling."""

import time
import json
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..models.chat_message import ChatMessage, MessageRole
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class ConversationState(dict):
    """State for conversation workflow."""
    pass


class LangChainChatService:
    """LangChain-based service for advanced conversation handling."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")

        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            max_tokens=settings.OPENAI_MAX_TOKENS
        )

        self.fast_llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",  # Faster model for simple tasks
            temperature=0.1,
            max_tokens=500
        )

        # Initialize conversation graph
        self.conversation_graph = self._build_conversation_graph()

    def _build_conversation_graph(self) -> StateGraph:
        """Build the conversation processing graph using LangGraph."""

        def analyze_intent(state: ConversationState) -> ConversationState:
            """Analyze user intent and categorize the query."""
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """Analyze the user's message and determine their intent.
                    Classify into one of these categories:
                    - plant_identification: User wants to identify a plant
                    - plant_care: User needs care advice (watering, light, fertilizing, etc.)
                    - plant_health: User has concerns about plant health, diseases, or problems
                    - general_question: General plant-related questions
                    - casual_conversation: Greetings, casual chat, off-topic

                    Respond with JSON: {{"intent": "category", "confidence": 0.0-1.0, "keywords": ["key", "words"]}}"""),
                    ("user", "{message}")
                ])

                chain = prompt | self.fast_llm | JsonOutputParser()
                result = chain.invoke({"message": state["user_message"]})

                state["intent"] = result.get("intent", "general_question")
                state["intent_confidence"] = result.get("confidence", 0.5)
                state["keywords"] = result.get("keywords", [])

                logger.info(f"Intent analysis: {state['intent']} (confidence: {state['intent_confidence']})")

            except Exception as e:
                logger.error(f"Intent analysis failed: {e}")
                state["intent"] = "general_question"
                state["intent_confidence"] = 0.3
                state["keywords"] = []

            return state

        def process_with_context(state: ConversationState) -> ConversationState:
            """Process the message with retrieved context and conversation history."""
            try:
                # Build conversation history for context
                conversation_context = ""
                if state.get("conversation_history"):
                    for msg in state["conversation_history"][-5:]:  # Last 5 messages
                        role = "Human" if msg.role == MessageRole.USER else "Assistant"
                        conversation_context += f"{role}: {msg.content}\n"

                # Build retrieved context
                context_text = ""
                if state.get("retrieved_context"):
                    context_items = []
                    for item in state["retrieved_context"]:
                        text = item.get("text", "")
                        source = item.get("metadata", {}).get("source", "knowledge_base")
                        context_items.append(f"[{source}] {text}")
                    context_text = "\n\n".join(context_items)

                # Build plant context
                plant_context = ""
                if state.get("plant_context"):
                    plant_context = f"User's plant information: {state['plant_context']}"

                # Create the main prompt based on intent
                system_prompt = self._get_system_prompt_for_intent(state["intent"])

                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("user", """
                    Current conversation:
                    {conversation_context}

                    Relevant context from knowledge base:
                    {context_text}

                    {plant_context}

                    User's current message: {user_message}

                    Respond in JSON format:
                    {{
                        "message": "Your helpful response",
                        "confidence": 0.0-1.0,
                        "suggestions": ["suggestion1", "suggestion2"],
                        "related_actions": ["action1", "action2"],
                        "requires_followup": true/false
                    }}
                    """)
                ])

                chain = prompt | self.llm | JsonOutputParser()
                result = chain.invoke({
                    "conversation_context": conversation_context,
                    "context_text": context_text,
                    "plant_context": plant_context,
                    "user_message": state["user_message"]
                })

                state["response"] = result.get("message", "I'm here to help with your plant questions!")
                state["confidence"] = result.get("confidence", 0.8)
                state["suggestions"] = result.get("suggestions", [])
                state["related_actions"] = result.get("related_actions", [])
                state["requires_followup"] = result.get("requires_followup", False)

            except Exception as e:
                logger.error(f"Context processing failed: {e}")
                state["response"] = self._get_fallback_response(state["intent"])
                state["confidence"] = 0.3
                state["suggestions"] = ["Can you provide more details?", "Would you like to try rephrasing your question?"]
                state["related_actions"] = []
                state["requires_followup"] = True

            return state

        def format_response(state: ConversationState) -> ConversationState:
            """Format the final response with suggestions and actions."""
            try:
                # Ensure we have minimum required fields
                if not state.get("response"):
                    state["response"] = "I'm here to help with your plant care questions!"

                if not state.get("suggestions"):
                    state["suggestions"] = self._get_default_suggestions(state["intent"])

                if not state.get("related_actions"):
                    state["related_actions"] = self._get_default_actions(state["intent"])

                # Add helpful follow-up based on intent
                if state["intent"] == "plant_health" and state.get("requires_followup"):
                    state["suggestions"].append("Consider uploading a photo for visual diagnosis")

                if state["intent"] == "plant_identification":
                    state["related_actions"].append("Upload a photo for identification")

                state["final_response"] = {
                    "message": state["response"],
                    "confidence": state.get("confidence", 0.8),
                    "suggestions": state["suggestions"][:3],  # Limit to 3 suggestions
                    "related_actions": state["related_actions"][:3],  # Limit to 3 actions
                    "processing_time": time.time() - state.get("start_time", time.time()),
                    "tokens_used": state.get("tokens_used", 0),
                    "model_used": settings.OPENAI_MODEL
                }

            except Exception as e:
                logger.error(f"Response formatting failed: {e}")
                state["final_response"] = {
                    "message": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                    "confidence": 0.1,
                    "suggestions": ["Try rephrasing your question", "Contact support if the issue persists"],
                    "related_actions": [],
                    "processing_time": time.time() - state.get("start_time", time.time()),
                    "tokens_used": 0,
                    "model_used": settings.OPENAI_MODEL
                }

            return state

        # Build the graph
        workflow = StateGraph(ConversationState)

        # Add nodes
        workflow.add_node("analyze_intent", analyze_intent)
        workflow.add_node("process_with_context", process_with_context)
        workflow.add_node("format_response", format_response)

        # Add edges
        workflow.add_edge("analyze_intent", "process_with_context")
        workflow.add_edge("process_with_context", "format_response")
        workflow.add_edge("format_response", END)

        # Set entry point
        workflow.set_entry_point("analyze_intent")

        # Compile with checkpointer for memory
        return workflow.compile(checkpointer=MemorySaver())

    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        retrieved_context: Optional[List[Dict[str, Any]]] = None,
        plant_context_id: Optional[int] = None,
        user_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using the conversation graph."""
        start_time = time.time()

        try:
            # Prepare initial state
            state = ConversationState({
                "user_message": message,
                "conversation_history": conversation_history or [],
                "retrieved_context": retrieved_context or [],
                "plant_context": user_context,
                "start_time": start_time
            })

            # Run the conversation graph
            result = await self.conversation_graph.ainvoke(
                state,
                config={"configurable": {"thread_id": f"plant_chat_{int(time.time())}"}}
            )

            return result["final_response"]

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                "message": "I apologize, but I'm experiencing technical difficulties. Please try your question again.",
                "confidence": 0.1,
                "suggestions": ["Try again in a moment", "Contact support if the issue persists"],
                "related_actions": [],
                "processing_time": time.time() - start_time,
                "tokens_used": 0,
                "model_used": settings.OPENAI_MODEL
            }

    async def generate_session_title(self, first_message: str) -> str:
        """Generate a concise title for a chat session."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Generate a short, descriptive title (2-6 words) for a plant care conversation based on the first message. Focus on the main topic."),
                ("user", "First message: {message}\n\nGenerate title:")
            ])

            chain = prompt | self.fast_llm
            result = chain.invoke({"message": first_message})

            title = result.content.strip().strip('"').strip("'")
            return title if len(title) <= 50 else first_message[:47] + "..."

        except Exception as e:
            logger.error(f"Title generation failed: {e}")
            return first_message[:47] + "..." if len(first_message) > 50 else first_message

    def _get_system_prompt_for_intent(self, intent: str) -> str:
        """Get system prompt based on detected intent."""
        prompts = {
            "plant_identification": """You are an expert botanist specializing in plant identification.
            Help users identify their plants using descriptions, photos, and characteristics.
            Provide scientific names, common names, and care tips for identified plants.
            Be conversational but accurate.""",

            "plant_care": """You are a knowledgeable plant care specialist.
            Provide practical, actionable advice for plant care including watering, lighting, fertilizing, repotting, and seasonal care.
            Tailor advice to the user's specific plant and situation.
            Be encouraging and supportive while being precise with care instructions.""",

            "plant_health": """You are a plant health expert and diagnostician.
            Help users identify and treat plant health issues, diseases, pests, and environmental problems.
            Provide step-by-step treatment plans and prevention strategies.
            When uncertain, recommend consulting with local experts or uploading photos for visual diagnosis.""",

            "general_question": """You are a friendly plant enthusiast and expert.
            Answer plant-related questions with enthusiasm and knowledge.
            Provide helpful information while encouraging the user's interest in plants.
            Feel free to share interesting plant facts and tips.""",

            "casual_conversation": """You are a friendly plant assistant.
            Engage naturally in conversation while gently steering towards plant-related topics.
            Be warm, helpful, and encouraging about plant care and gardening."""
        }

        return prompts.get(intent, prompts["general_question"])

    def _get_fallback_response(self, intent: str) -> str:
        """Get fallback response based on intent."""
        responses = {
            "plant_identification": "I'd be happy to help identify your plant! Can you describe what it looks like or upload a photo?",
            "plant_care": "I'm here to help with plant care advice! What specific care question do you have about your plant?",
            "plant_health": "I can help diagnose plant health issues. Can you describe the symptoms you're seeing?",
            "general_question": "I'm here to help with any plant-related questions you might have!",
            "casual_conversation": "Hello! I'm your plant care assistant. How can I help you with your plants today?"
        }

        return responses.get(intent, "I'm here to help with your plant questions! What would you like to know?")

    def _get_default_suggestions(self, intent: str) -> List[str]:
        """Get default suggestions based on intent."""
        suggestions = {
            "plant_identification": [
                "Describe the leaves and growth pattern",
                "Upload a photo if possible",
                "Tell me about the plant's size and location"
            ],
            "plant_care": [
                "What's your current care routine?",
                "Tell me about your plant's environment",
                "Any specific concerns about your plant?"
            ],
            "plant_health": [
                "Describe the symptoms in detail",
                "When did you first notice the problem?",
                "Upload a photo for visual diagnosis"
            ],
            "general_question": [
                "Ask about specific plant care topics",
                "Get help identifying a plant",
                "Learn about plant health and problems"
            ],
            "casual_conversation": [
                "Ask about plant care tips",
                "Get help with plant problems",
                "Learn about different plant species"
            ]
        }

        return suggestions.get(intent, ["How can I help with your plants?"])

    def _get_default_actions(self, intent: str) -> List[str]:
        """Get default actions based on intent."""
        actions = {
            "plant_identification": [
                "Upload plant photo",
                "Browse plant database",
                "Learn about plant species"
            ],
            "plant_care": [
                "Set care reminders",
                "View care calendar",
                "Track plant progress"
            ],
            "plant_health": [
                "Schedule plant checkup",
                "Upload problem photo",
                "Find local plant experts"
            ],
            "general_question": [
                "Explore plant care guides",
                "Browse plant species",
                "Set up plant tracking"
            ],
            "casual_conversation": [
                "Ask about plant care",
                "Explore plant identification",
                "Learn plant facts"
            ]
        }

        return actions.get(intent, ["Explore plant features"])
