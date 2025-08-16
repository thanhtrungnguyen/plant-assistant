# backend/src/app/services/podcast_service.py

import logging

from .schemas import GeneratePodcastInput, PodcastUserContext
from .context_service import PodcastContextService
from .utils import (
    get_weather,
    generate_contextual_podcast,
    synthesize_edge_tts,
)

logger = logging.getLogger(__name__)


async def create_podcast_for_user(input: GeneratePodcastInput) -> bytes:
    """
    Create a personalized podcast using user context from Pinecone.

    Args:
        input: Podcast generation input with user_id and location

    Returns:
        bytes: Audio bytes of the generated podcast
    """
    try:
        # Initialize context service
        context_service = PodcastContextService()

        # Convert user_id to int for context service
        user_id_int = input.user_id  # user_id is now an int directly from database

        # Get weather info if location is provided
        weather_info = None
        location_context = None
        if input.location:
            location_str = f"{input.location.latitude},{input.location.longitude}"
            weather_info = get_weather(location_str)
            location_context = f"Location: {location_str}, Weather: {weather_info}"

        # Retrieve user context from Pinecone
        user_context = await context_service.retrieve_podcast_context(
            user_id=user_id_int,
            location_context=location_context,
            top_k=8,  # Get more context for richer podcasts
        )

        # Generate seasonal recommendations if we have plant and weather data
        seasonal_recommendations = []
        if user_context.plants_owned and (weather_info or location_context):
            seasonal_recommendations = (
                await context_service.get_seasonal_recommendations(
                    user_plants=user_context.plants_owned, weather_info=weather_info
                )
            )

        # Generate podcast script using rich context
        podcast_text = await generate_contextual_podcast(
            user_context=user_context,
            weather_info=weather_info,
            seasonal_recommendations=seasonal_recommendations,
        )

        # Convert the podcast script to audio bytes
        audio_bytes = await synthesize_edge_tts(podcast_text)

        logger.info(
            f"Successfully generated contextual podcast for user {input.user_id}"
        )
        return audio_bytes

    except Exception as e:
        logger.error(
            f"Failed to create contextual podcast for user {input.user_id}: {e}"
        )
        # Fallback to basic podcast generation if context fails
        return await _create_fallback_podcast(input)


async def _create_fallback_podcast(input: GeneratePodcastInput) -> bytes:
    """Create a basic podcast when context retrieval fails."""
    try:
        # Get weather info if available
        weather_info = None
        if input.location:
            location_str = f"{input.location.latitude},{input.location.longitude}"
            weather_info = get_weather(location_str)

        # Create basic context for fallback
        fallback_context = PodcastUserContext(
            user_id=input.user_id,  # Use the actual user_id
            plants_owned=["houseplants"],
            common_care_issues=[],
            recent_recommendations=[],
            care_preferences=["beginner-friendly care"],
            experience_level="beginner",
            recent_diagnoses=[],
            context_confidence=0.0,
            last_updated="",
        )

        # Generate basic podcast
        podcast_text = await generate_contextual_podcast(
            user_context=fallback_context,
            weather_info=weather_info,
            seasonal_recommendations=[],
        )

        audio_bytes = await synthesize_edge_tts(podcast_text)

        logger.info(f"Generated fallback podcast for user {input.user_id}")
        return audio_bytes

    except Exception as e:
        logger.error(f"Failed to create fallback podcast for user {input.user_id}: {e}")
        raise


async def get_user_context_summary(user_id: int) -> dict:
    """Get a summary of user context for debugging/validation."""
    try:
        context_service = PodcastContextService()
        user_id_int = user_id  # Use the actual database user_id
        context = await context_service.retrieve_podcast_context(user_id_int)

        return {
            "user_id": str(user_id),
            "plants_count": len(context.plants_owned),
            "plants": context.plants_owned,
            "experience_level": context.experience_level,
            "common_issues": context.common_care_issues,
            "context_confidence": context.context_confidence,
            "has_recent_diagnoses": len(context.recent_diagnoses) > 0,
        }

    except Exception as e:
        logger.error(f"Failed to get context summary for user {user_id}: {e}")
        return {"error": str(e)}
