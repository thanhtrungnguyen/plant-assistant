"""
Plant Diagnosis Service using LangGraph Multi-Agent System

This module implements a multi-agent system for plant diagnosis with the following agents:
1. Input Validator - Validates if the image is a legal plant
2. Plant Identifier - Identifies the plant species
3. Condition Analyzer - Diagnoses plant health condition
4. Action Plan Generator - Creates treatment action plan
5. Output Formatter - Formats final JSON response
6. Master Agent - Orchestrates the entire workflow
"""

import base64
import json
from typing import Dict, List, Optional, TypedDict, Any
from PIL import Image
import io

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.config import settings


class DiagnosisState(TypedDict):
    """State shared between agents in the diagnosis workflow"""

    image_data: str  # Base64 encoded image
    validation_result: Optional[bool]
    plant_name: Optional[str]
    condition: Optional[str]
    detail_diagnosis: Optional[str]
    action_plan: Optional[List[Dict[str, Any]]]
    error: Optional[str]
    final_output: Optional[Dict[str, Any]]


class PlantDiagnosisService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")

        # Initialize OpenAI client (unified model for text and vision)
        self.llm = ChatOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )

        # Build the workflow graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with all agents"""
        workflow = StateGraph(DiagnosisState)

        # Add all agent nodes
        workflow.add_node("input_validator", self._input_validator)
        workflow.add_node("plant_identifier", self._plant_identifier)
        workflow.add_node("condition_analyzer", self._condition_analyzer)
        workflow.add_node("action_plan_generator", self._action_plan_generator)
        workflow.add_node("output_formatter", self._output_formatter)
        workflow.add_node("error_handler", self._error_handler)

        # Set entry point
        workflow.set_entry_point("input_validator")

        # Add conditional edges based on validation result
        workflow.add_conditional_edges(
            "input_validator",
            self._should_continue_after_validation,
            {"continue": "plant_identifier", "error": "error_handler"},
        )

        # Sequential flow after successful validation
        workflow.add_conditional_edges(
            "plant_identifier",
            self._should_continue_after_identification,
            {"continue": "condition_analyzer", "error": "error_handler"},
        )
        workflow.add_edge("condition_analyzer", "action_plan_generator")
        workflow.add_edge("action_plan_generator", "output_formatter")

        # Terminal nodes
        workflow.add_edge("output_formatter", END)
        workflow.add_edge("error_handler", END)

        return workflow

    async def _input_validator(self, state: DiagnosisState) -> DiagnosisState:
        """Agent 1: Validates if the image contains a valid plant"""
        try:
            # Validate image format and content
            image_data = state["image_data"]
            if not image_data:
                state["error"] = "No image data provided"
                state["validation_result"] = False
                return state

            # Decode and validate image
            try:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))

                # Basic image validation
                if image.size[0] < 100 or image.size[1] < 100:
                    state["error"] = "Image too small (minimum 100x100 pixels)"
                    state["validation_result"] = False
                    return state

            except Exception as e:
                state["error"] = f"Invalid image format: {str(e)}"
                state["validation_result"] = False
                return state

            # Use Vision API to validate if image contains a plant
            validation_prompt = SystemMessage(
                content="""
You are a plant image validator with expertise in botany and plant identification. Analyze the image carefully to determine if it contains a valid plant for diagnosis.

Respond with ONLY one of these exact responses:
- "VALID_PLANT" if the image contains a real, living plant that is legal and appropriate for care assistance
- "INVALID_NOT_PLANT" if the image doesn't contain a plant or contains artificial/fake plants
- "INVALID_ILLEGAL_PLANT" if the image contains illegal or controlled substance plants (cannabis, poppy, coca, etc.)
- "INVALID_INAPPROPRIATE" if the image contains inappropriate, harmful, or unrelated content
- "INVALID_UNCLEAR" if the image is too blurry/unclear to properly identify

Validation Rules:
✅ ACCEPT: Houseplants, garden plants, vegetables, herbs (basil, mint, oregano), fruit trees, ornamental plants, flowers, succulents, trees, shrubs
❌ REJECT: Cannabis/marijuana, opium poppy, coca plants, any controlled substance plants
❌ REJECT: Artificial/fake plants, drawings, paintings, toys, non-plant objects
❌ REJECT: Images that are blurry, dark, or unclear
❌ REJECT: Inappropriate, harmful, or completely unrelated content

Be thorough in your analysis - examine leaves, stems, flowers, and overall plant structure. Many legitimate plants may have similar leaf shapes, so focus on the complete plant characteristics and context.
"""
            )

            human_message = HumanMessage(
                content=[
                    {"type": "text", "text": "Is this a valid plant image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ]
            )

            response = await self.llm.ainvoke([validation_prompt, human_message])
            validation_result = response.content.strip()

            if validation_result == "VALID_PLANT":
                state["validation_result"] = True
            else:
                state["validation_result"] = False
                error_messages = {
                    "INVALID_NOT_PLANT": "Image does not contain a plant or contains artificial/fake plants",
                    "INVALID_ILLEGAL_PLANT": "Cannot provide assistance for illegal or controlled substance plants",
                    "INVALID_INAPPROPRIATE": "Inappropriate content detected",
                    "INVALID_UNCLEAR": "Image is too unclear for analysis",
                }
                state["error"] = error_messages.get(
                    validation_result,
                    "Invalid image - please upload a clear photo of a legal plant",
                )

            return state

        except Exception as e:
            state["error"] = f"Validation error: {str(e)}"
            state["validation_result"] = False
            return state

    async def _plant_identifier(self, state: DiagnosisState) -> DiagnosisState:
        """Agent 2: Identifies the plant species"""
        try:
            identification_prompt = SystemMessage(
                content="""
You are a professional botanist specializing in plant identification for care assistance.
Analyze the provided plant image and identify the species.

IMPORTANT: If you identify any illegal or controlled substance plants (cannabis, marijuana, opium poppy, coca, etc.),
respond with "ILLEGAL_PLANT_DETECTED" instead of the plant name.

For legal plants, respond with ONLY the common name. Examples:
- "Monstera Deliciosa"
- "Snake Plant"
- "Peace Lily"
- "Fiddle Leaf Fig"
- "Apple Tree"
- "Basil"
- "Tomato Plant"

If you cannot identify the specific species, provide the closest genus or family name.
If completely uncertain, respond with "Unknown Plant Species".
"""
            )

            human_message = HumanMessage(
                content=[
                    {"type": "text", "text": "Please identify this plant species."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{state['image_data']}"
                        },
                    },
                ]
            )

            response = await self.llm.ainvoke([identification_prompt, human_message])
            plant_name = response.content.strip()

            # Secondary check for illegal plants
            if plant_name == "ILLEGAL_PLANT_DETECTED":
                state["error"] = (
                    "Cannot provide assistance for illegal or controlled substance plants"
                )
                return state

            state["plant_name"] = plant_name
            return state

        except Exception as e:
            state["error"] = f"Plant identification error: {str(e)}"
            return state

    async def _condition_analyzer(self, state: DiagnosisState) -> DiagnosisState:
        """Agent 3: Analyzes plant health condition and provides diagnosis"""
        try:
            plant_name = state.get("plant_name", "Unknown Plant")

            diagnosis_prompt = SystemMessage(
                content=f"""
You are a plant pathologist analyzing the health of a {plant_name}.
Examine the image for signs of disease, pests, nutrient deficiencies, or other health issues.

Provide your analysis in exactly this format:
CONDITION: [One word/short phrase: "Healthy", "Overwatered", "Underwatered", "Pest Infestation", "Nutrient Deficiency", "Disease", etc.]
DIAGNOSIS: [2-3 detailed sentences explaining what you observe, the likely cause, and severity]

Focus on visible symptoms like leaf discoloration, wilting, spots, pests, or growth abnormalities.
If the plant appears healthy, state "Healthy" and describe positive signs.
"""
            )

            human_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"Please diagnose the health condition of this {plant_name}.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{state['image_data']}"
                        },
                    },
                ]
            )

            response = await self.llm.ainvoke([diagnosis_prompt, human_message])
            diagnosis_text = response.content.strip()

            # Parse the structured response
            lines = diagnosis_text.split("\n")
            condition = "Unknown"
            detail_diagnosis = diagnosis_text

            for line in lines:
                if line.startswith("CONDITION:"):
                    condition = line.replace("CONDITION:", "").strip()
                elif line.startswith("DIAGNOSIS:"):
                    detail_diagnosis = line.replace("DIAGNOSIS:", "").strip()

            state["condition"] = condition
            state["detail_diagnosis"] = detail_diagnosis
            return state

        except Exception as e:
            state["error"] = f"Condition analysis error: {str(e)}"
            return state

    async def _action_plan_generator(self, state: DiagnosisState) -> DiagnosisState:
        """Agent 4: Generates action plan based on diagnosis"""
        try:
            plant_name = state.get("plant_name", "Unknown Plant")
            condition = state.get("condition", "Unknown")
            diagnosis = state.get("detail_diagnosis", "")

            action_prompt = SystemMessage(
                content=f"""
You are a plant care specialist. Based on the diagnosis of a {plant_name} with condition "{condition}",
provide a specific action plan.

Create 3-5 actionable steps to address the plant's needs. Format as a JSON array:
[
  {{"id": 1, "action": "Specific action step 1"}},
  {{"id": 2, "action": "Specific action step 2"}},
  ...
]

Make actions specific, practical, and immediately actionable. Include timeframes when relevant.
Examples: "Water thoroughly until drainage occurs", "Move to bright, indirect light", "Apply neem oil spray every 3 days"

Diagnosis context: {diagnosis}
"""
            )

            human_message = HumanMessage(
                content=f"Create an action plan for {plant_name} with {condition}"
            )

            response = await self.llm.ainvoke([action_prompt, human_message])
            action_plan_text = response.content.strip()

            # Parse JSON response
            try:
                # Extract JSON from response if wrapped in markdown
                if "```json" in action_plan_text:
                    action_plan_text = (
                        action_plan_text.split("```json")[1].split("```")[0].strip()
                    )
                elif "```" in action_plan_text:
                    action_plan_text = action_plan_text.split("```")[1].strip()

                action_plan = json.loads(action_plan_text)

                # Validate structure
                if not isinstance(action_plan, list):
                    raise ValueError("Action plan must be a list")

                for i, action in enumerate(action_plan):
                    if (
                        not isinstance(action, dict)
                        or "id" not in action
                        or "action" not in action
                    ):
                        raise ValueError(f"Invalid action format at index {i}")

                state["action_plan"] = action_plan

            except json.JSONDecodeError:
                # Fallback: create structured plan from text
                fallback_plan = [
                    {
                        "id": 1,
                        "action": "Follow general care guidelines for the diagnosed condition",
                    },
                    {"id": 2, "action": "Monitor plant closely for changes"},
                    {"id": 3, "action": "Adjust care routine based on plant response"},
                ]
                state["action_plan"] = fallback_plan

            return state

        except Exception as e:
            state["error"] = f"Action plan generation error: {str(e)}"
            return state

    async def _output_formatter(self, state: DiagnosisState) -> DiagnosisState:
        """Agent 5: Formats the final JSON output"""
        try:
            final_output = {
                "plant_name": state.get("plant_name", "Unknown Plant"),
                "condition": state.get("condition", "Unknown"),
                "detail_diagnosis": state.get(
                    "detail_diagnosis", "Unable to provide diagnosis"
                ),
                "action_plan": state.get("action_plan", []),
            }

            state["final_output"] = final_output
            return state

        except Exception as e:
            state["error"] = f"Output formatting error: {str(e)}"
            return state

    async def _error_handler(self, state: DiagnosisState) -> DiagnosisState:
        """Handles errors and creates error response"""
        error_output = {
            "error": "diagnosis_failed",
            "message": state.get(
                "error", "Unknown error occurred during plant diagnosis"
            ),
        }
        state["final_output"] = error_output
        return state

    def _should_continue_after_validation(self, state: DiagnosisState) -> str:
        """Conditional routing after validation"""
        if state.get("validation_result", False):
            return "continue"
        else:
            return "error"

    def _should_continue_after_identification(self, state: DiagnosisState) -> str:
        """Conditional routing after plant identification"""
        if state.get("error"):
            return "error"
        else:
            return "continue"

    async def diagnose_plant(self, image_data: str) -> Dict[str, Any]:
        """
        Main method to diagnose a plant from image data

        Args:
            image_data: Base64 encoded image string

        Returns:
            Dict containing diagnosis result or error
        """
        try:
            # Initialize state
            initial_state = {
                "image_data": image_data,
                "validation_result": None,
                "plant_name": None,
                "condition": None,
                "detail_diagnosis": None,
                "action_plan": None,
                "error": None,
                "final_output": None,
            }

            # Run the workflow
            config = {"configurable": {"thread_id": "diagnosis_session"}}
            final_state = await self.app.ainvoke(initial_state, config)

            return final_state.get(
                "final_output",
                {
                    "error": "workflow_failed",
                    "message": "Diagnosis workflow failed to complete",
                },
            )

        except Exception as e:
            return {
                "error": "service_error",
                "message": f"Plant diagnosis service error: {str(e)}",
            }


# Global service instance
diagnosis_service = None


def get_diagnosis_service() -> PlantDiagnosisService:
    """Dependency injection for diagnosis service"""
    global diagnosis_service
    if diagnosis_service is None:
        diagnosis_service = PlantDiagnosisService()
    return diagnosis_service
