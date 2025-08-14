# backend/src/app/services/podcast_service.py

from .schemas import GeneratePodcastInput
from .utils import get_weather, generate_podcast, text_to_wav_bytes, generate_dummy_data


async def create_podcast_for_user(input: GeneratePodcastInput) -> bytes:
    try:
        location_str: str
        user_data = generate_dummy_data(input.user_id)
        if not user_data:
            raise ValueError("User does not exist")

        if input.location:
            location_str = f"{input.location.latitude},{input.location.longitude}"
        else:
            location_str = user_data.address

        weather_info = get_weather(location_str)
        podcast_text = generate_podcast(
            user_data.userName, weather_info, user_data.plants
        )

        # 2. Convert text to WAV bytes
        audio_bytes = text_to_wav_bytes(podcast_text)

        # 3. Return audio file response
        return audio_bytes
    except Exception as e:
        print("Error in create_podcast_for_user:", e)
        raise
