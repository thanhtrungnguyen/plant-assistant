# backend/src/app/routes/podcast.py

from fastapi import APIRouter, Depends, HTTPException
from .schemas import GeneratePodcastInput
from .service import create_podcast_for_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Response, HTTPException


router = APIRouter()


@router.post("/generate_podcast")
async def generate_podcast(input: GeneratePodcastInput):
    try:
        audio_bytes = await create_podcast_for_user(input)
        if audio_bytes is None:
            raise HTTPException(status_code=500, detail="Empty audio returned from podcast generator")
        return Response(content=audio_bytes, media_type="audio/wav")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # You can add logging here if needed
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the podcast: {e}")
