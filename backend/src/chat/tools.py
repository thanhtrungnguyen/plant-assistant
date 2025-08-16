"""LangGraph tools for plant assistant chatbot."""

import json
import logging
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Global state holder for accessing image data in tools
_current_state = None


def set_current_state(state):
    """Set the current conversation state for tools to access."""
    global _current_state
    _current_state = state


def get_current_state():
    """Get the current conversation state."""
    global _current_state
    return _current_state


@tool
async def diagnose_plant_from_image(
    image_description: str,
    symptoms: str = "",
    user_id: str = "anonymous",
    user_preferences: Optional[str] = None,
) -> str:
    """
    Analyze plant health from an uploaded image using visual AI analysis.
    Use this tool when the user has uploaded an image of their plant.

    Args:
        image_description: Description of what the user is asking about the plant image
        symptoms: User-reported symptoms (optional)
        user_id: User identifier for personalization
        user_preferences: JSON string of user preferences and context

    Returns:
        JSON string with visual analysis results including plant identification and health assessment.
    """
    try:
        logger.info(f"🔧 IMAGE DIAGNOSIS TOOL CALLED! user: {user_id}")

        # Get image data from the current state
        current_state = get_current_state()
        image_base64 = None

        if current_state:
            image_base64 = current_state.get("image_data")

        from diagnosis.service import get_diagnosis_service

        if not image_base64:
            return json.dumps(
                {
                    "success": False,
                    "analysis_type": "image_error",
                    "error": "No image data provided",
                    "message": "I need an image to perform visual analysis. Please upload a photo of your plant.",
                    "plant_identification": {
                        "plant_name": "Unknown",
                        "confidence": 0.0,
                    },
                    "health_assessment": {
                        "condition": "Error",
                        "diagnosis": "No image provided",
                    },
                    "treatment_recommendations": [],
                }
            )

        # Parse user preferences if provided
        preferences = {}
        if user_preferences:
            try:
                preferences = json.loads(user_preferences)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse user preferences: {user_preferences}")

        # Call the diagnosis API for image analysis
        diagnosis_service = get_diagnosis_service()
        api_result = await diagnosis_service.diagnose_plant(image_base64)

        # Format API result to match expected response structure
        response = {
            "success": True,
            "analysis_type": "visual_api",
            "message": api_result.get("analysis", "Visual analysis completed"),
            "plant_identification": {
                "plant_name": api_result.get("plant_name", "Unknown"),
                "confidence": api_result.get("confidence", 0.0),
                "species": api_result.get(
                    "species", api_result.get("plant_name", "Unknown")
                ),
            },
            "health_assessment": {
                "condition": api_result.get("condition", "Unknown"),
                "diagnosis": api_result.get(
                    "diagnosis", api_result.get("analysis", "")
                ),
                "severity": api_result.get("severity", "Unknown"),
            },
            "treatment_recommendations": api_result.get("recommendations", []),
            "confidence_score": api_result.get("confidence", 0.0),
            "user_notes": symptoms,
            "api_response": api_result,
        }

        return json.dumps(response, indent=2)

    except Exception as e:
        logger.error(f"Image diagnosis tool error: {e}")
        error_response = {
            "success": False,
            "analysis_type": "image_error",
            "error": str(e),
            "message": "I encountered an issue analyzing the plant image. Please try again or provide more details.",
            "plant_identification": {"plant_name": "Unknown", "confidence": 0.0},
            "health_assessment": {"condition": "Error", "diagnosis": str(e)},
            "treatment_recommendations": [],
        }
        return json.dumps(error_response, indent=2)


@tool
async def diagnose_plant_from_text(
    plant_description: str,
    symptoms: str = "",
    user_id: str = "anonymous",
    user_preferences: Optional[str] = None,
) -> str:
    """
    Provide plant care advice and diagnosis based on text descriptions using our knowledge database.
    Use this tool when the user describes their plant or symptoms in text without uploading an image.

    Args:
        plant_description: Description of the plant or the question being asked
        symptoms: User-reported symptoms (optional)
        user_id: User identifier for personalization
        user_preferences: JSON string of user preferences and context

    Returns:
        JSON string with knowledge-based diagnosis and care recommendations.
    """
    try:
        logger.info(f"🔧 TEXT DIAGNOSIS TOOL CALLED! user: {user_id}")

        # Import here to avoid circular dependency
        from .services.diagnosis_context_service import PlantDiagnosisContextService

        # Parse user preferences if provided
        preferences = {}
        if user_preferences:
            try:
                preferences = json.loads(user_preferences)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse user preferences: {user_preferences}")

        # Use context-based diagnosis service
        diagnosis_context_service = PlantDiagnosisContextService()

        # Query Pinecone for similar diagnosis cases
        context_results = await diagnosis_context_service.query_diagnosis_context(
            image_description=plant_description,
            symptoms=symptoms,
            user_id=user_id,
            top_k=5,
        )

        if not context_results:
            # Use fallback when no context is available
            fallback_response = await diagnosis_context_service.get_fallback_diagnosis(
                image_description=plant_description, symptoms=symptoms
            )
            return json.dumps(
                {
                    "success": False,
                    "analysis_type": "context_fallback",
                    "context_available": False,
                    "message": fallback_response,
                    "plant_identification": {
                        "plant_name": "Unknown",
                        "confidence": 0.0,
                    },
                    "health_assessment": {
                        "condition": "Unable to determine",
                        "diagnosis": fallback_response,
                    },
                    "treatment_recommendations": [],
                    "context_sources": 0,
                },
                indent=2,
            )

        # Aggregate context from multiple cases
        aggregated_context = (
            await diagnosis_context_service.aggregate_diagnosis_context(context_results)
        )

        # Generate personalized diagnosis response
        diagnosis_response = await diagnosis_context_service.generate_context_diagnosis(
            aggregated_context=aggregated_context,
            user_preferences=preferences,
            image_description=plant_description,
            symptoms=symptoms,
        )

        # Format response in expected structure
        response = {
            "success": True,
            "analysis_type": "context_based",
            "context_available": True,
            "message": diagnosis_response,
            "plant_identification": {
                "plant_name": aggregated_context.get("plant_name", "Unknown"),
                "confidence": aggregated_context.get("confidence", 0.0),
                "species": aggregated_context.get("plant_name", "Unknown"),
            },
            "health_assessment": {
                "condition": aggregated_context.get("condition", "Unknown"),
                "diagnosis": diagnosis_response,
                "severity": "Moderate"
                if aggregated_context.get("condition", "").lower()
                not in ["healthy", "unknown"]
                else "None",
            },
            "treatment_recommendations": [
                {"id": i + 1, "action": treatment}
                for i, treatment in enumerate(aggregated_context.get("treatments", []))
            ],
            "context_sources": aggregated_context.get("similar_cases_count", 0),
            "confidence_score": aggregated_context.get("confidence", 0.0),
            "user_notes": symptoms,
        }

        return json.dumps(response, indent=2)

    except Exception as e:
        logger.error(f"Text diagnosis tool error: {e}")
        error_response = {
            "success": False,
            "analysis_type": "context_error",
            "error": str(e),
            "message": "I encountered an issue searching our knowledge database. Please try rephrasing your question or provide more details.",
            "plant_identification": {"plant_name": "Unknown", "confidence": 0.0},
            "health_assessment": {"condition": "Error", "diagnosis": str(e)},
            "treatment_recommendations": [],
            "context_sources": 0,
        }
        return json.dumps(error_response, indent=2)


# List of available tools for the LangGraph agent
PLANT_TOOLS = [diagnose_plant_from_image, diagnose_plant_from_text]
