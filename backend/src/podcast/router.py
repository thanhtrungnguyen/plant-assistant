# backend/src/app/routes/podcast.py

from fastapi import APIRouter, HTTPException
from .schemas import GeneratePodcastInput
from .service import create_podcast_for_user
from .utils import text_to_wav_bytes
from fastapi import Response
from pydantic import BaseModel
from typing import Literal


router = APIRouter()


class TestVoiceInput(BaseModel):
    text: str = "Xin chào! Đây là test giọng nói cho podcast về cây xanh."
    voice_type: Literal["female", "female_soft", "female_energetic"] = "female"


@router.post("/generate_podcast")
async def generate_podcast(input: GeneratePodcastInput):
    try:
        audio_bytes = await create_podcast_for_user(input)
        if audio_bytes is None:
            raise HTTPException(
                status_code=500, detail="Empty audio returned from podcast generator"
            )
        return Response(content=audio_bytes, media_type="audio/wav")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # You can add logging here if needed
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the podcast: {e}",
        )


@router.post("/test_voice")
async def test_voice(input: TestVoiceInput):
    """
    Endpoint test để thử các loại giọng nói khác nhau
    """
    try:
        audio_bytes = text_to_wav_bytes(input.text, input.voice_type)
        if audio_bytes is None:
            raise HTTPException(
                status_code=500, detail="Empty audio returned from voice generator"
            )
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while testing voice: {e}",
        )
