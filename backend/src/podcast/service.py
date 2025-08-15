# backend/src/app/services/podcast_service.py

from .schemas import GeneratePodcastInput
from .utils import get_weather, generate_podcast, text_to_wav_bytes, generate_dummy_data,synthesize_edge_tts


async def create_podcast_for_user(input: GeneratePodcastInput) -> bytes:
    try:
        # Retrieve user data (dummy data for now)
        user_data = generate_dummy_data(input.user_id)
        if not user_data:
            raise ValueError("User does not exist")

        # Get weather info if location is provided
        weather_info = None
        if input.location:
            location_str = f"{input.location.latitude},{input.location.longitude}"
            weather_info = get_weather(location_str)

        # Generate podcast script using user and weather data
        podcast_text = generate_podcast(
            user_data.userName,
            weather_info,
            user_data.plants
        )

        # Convert the podcast script to WAV audio bytes
        audio_bytes = await synthesize_edge_tts(podcast_text)

        return audio_bytes

    except Exception as e:
        # Log and re-raise the exception
        print(f"[ERROR] Failed to create podcast for user {input.user_id}: {e}")
        raise

