# backend/src/app/routes/podcast.py

from fastapi import APIRouter, HTTPException, Depends
from .schemas import GeneratePodcastInput, GeneratePodcastRequest
from .service import create_podcast_for_user, get_user_context_summary
from fastapi import Response
from src.auth.dependencies import require_user
from src.auth.models import User


router = APIRouter()


@router.post("/generate_podcast")
async def generate_podcast(
    request_data: GeneratePodcastRequest, current_user: User = Depends(require_user)
):
    """Generate a personalized podcast using user context from Pinecone."""
    try:
        # Create input with authenticated user's ID
        input = GeneratePodcastInput(
            user_id=current_user.id,  # Use actual database user ID
            location=request_data.location,
        )

        audio_bytes = await create_podcast_for_user(input)
        if audio_bytes is None:
            raise HTTPException(
                status_code=500, detail="Empty audio returned from podcast generator"
            )
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        # You can add logging here if needed
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the podcast: {e}",
        )


@router.get("/user_context")
async def get_user_context_summary_endpoint(current_user: User = Depends(require_user)):
    """Get a summary of user context for debugging/validation."""
    try:
        context_summary = await get_user_context_summary(current_user.id)
        return context_summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving user context: {e}",
        )
