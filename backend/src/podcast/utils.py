"""Enhanced utilities for contextual podcast generation."""

import logging
from typing import Optional, List
from openai import OpenAI
import requests
import torch
from transformers import VitsModel, AutoTokenizer
import io
import torchaudio
import edge_tts
from pydub import AudioSegment
from fastapi.routing import APIRoute

from ..core.config import settings
from .schemas import UserData, PodcastUserContext

logger = logging.getLogger(__name__)

# Initialize models
model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")

# Initialize OpenAI client
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
)


def simple_generate_unique_route_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


def get_weather(location_str: str) -> str:
    """Get weather information for a given location."""
    url = f"http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={location_str}&lang=vi"
    response = requests.get(url)
    data = response.json()
    condition = data["current"]["condition"]["text"]
    location_name = data["location"]["name"]
    temp = data["current"]["temp_c"]
    return f"Thời tiết hôm nay tại {location_name}: {condition}, nhiệt độ {temp}°C."


async def generate_contextual_podcast(
    user_context: PodcastUserContext,
    weather_info: Optional[str] = None,
    seasonal_recommendations: Optional[List[str]] = None,
) -> str:
    """
    Generate a personalized podcast script based on user context.

    Args:
        user_context: Rich user context from Pinecone
        weather_info: Current weather information
        seasonal_recommendations: Seasonal care recommendations

    Returns:
        str: Generated podcast script
    """
    try:
        # Build personalized prompt based on user context
        prompt = _build_contextual_prompt(
            user_context=user_context,
            weather_info=weather_info,
            seasonal_recommendations=seasonal_recommendations or [],
        )

        # Generate podcast using OpenAI
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": _get_system_prompt(user_context.experience_level),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,  # Slightly more creative for podcast content
            max_tokens=500,  # Limit for podcast length
        )

        podcast_text = (
            response.choices[0].message.content
            or "Không thể tạo podcast hôm nay, vui lòng thử lại sau."
        )

        logger.info(f"Generated contextual podcast for user {user_context.user_id}")
        return podcast_text

    except Exception as e:
        logger.error(f"Error generating contextual podcast: {e}")
        # Fallback to basic podcast
        return _generate_basic_podcast(weather_info)


def _build_contextual_prompt(
    user_context: PodcastUserContext,
    weather_info: Optional[str] = None,
    seasonal_recommendations: Optional[List[str]] = None,
) -> str:
    """Build a personalized prompt based on user context."""

    # Start with user's plants
    plants_section = ""
    if user_context.plants_owned and user_context.plants_owned != ["houseplants"]:
        plants_list = ", ".join(user_context.plants_owned[:3])  # Top 3 plants
        plants_section = f"- Cây trồng của bạn: {plants_list}\n"
    else:
        plants_section = "- Cây cảnh trong nhà của bạn\n"

    # Weather section
    weather_section = ""
    if weather_info:
        weather_section = f"- Thời tiết hôm nay: {weather_info}\n"
    else:
        weather_section = (
            "- Thông tin thời tiết không có sẵn - tập trung vào lời khuyên chung\n"
        )

    # Recent issues and recommendations
    issues_section = ""
    if user_context.common_care_issues:
        issues_list = ", ".join(user_context.common_care_issues[:2])
        issues_section = f"- Những vấn đề chăm sóc gần đây: {issues_list}\n"

    recommendations_section = ""
    if user_context.recent_recommendations:
        rec_list = ", ".join(user_context.recent_recommendations[:2])
        recommendations_section = f"- Lời khuyên đã được đưa ra: {rec_list}\n"

    # Seasonal recommendations
    seasonal_section = ""
    if seasonal_recommendations and len(seasonal_recommendations) > 0:
        seasonal_list = ". ".join(seasonal_recommendations[:2])
        seasonal_section = f"- Lời khuyên theo mùa: {seasonal_list}\n"

    # User preferences
    preferences_section = ""
    if user_context.care_preferences:
        pref_text = ". ".join(user_context.care_preferences[:2])
        preferences_section = f"- Sở thích chăm sóc: {pref_text}\n"

    # Recent diagnoses
    diagnoses_section = ""
    if user_context.recent_diagnoses:
        diagnoses_section = "- Đã có phân tích tình trạng cây gần đây\n"

    # Build complete prompt
    prompt = (
        f"Hãy viết một đoạn podcast ngắn (khoảng 45-60 giây) được cá nhân hóa, bao gồm:\n\n"
        f"{plants_section}"
        f"{weather_section}"
        f"{issues_section}"
        f"{recommendations_section}"
        f"{seasonal_section}"
        f"{preferences_section}"
        f"{diagnoses_section}"
        f"\nYêu cầu:\n"
        f"- Tập trung vào những việc cụ thể nên làm trong ngày\n"
        f"- Đưa ra lời khuyên thiết thực và có thể thực hiện được\n"
        f"- Phù hợp với trình độ {user_context.experience_level}\n"
        f"- Văn phong thân thiện, truyền cảm hứng\n"
        f"- Khiến người nghe cảm thấy kết nối với cây cối\n"
    )

    return prompt


def _get_system_prompt(experience_level: str) -> str:
    """Get system prompt based on user experience level."""

    base_prompt = (
        "Bạn là một chuyên gia podcast về chăm sóc cây trồng. "
        "Hãy tạo ra một đoạn podcast ngắn, cá nhân hóa, truyền cảm hứng và hữu ích."
    )

    if experience_level == "beginner":
        return base_prompt + (
            " Người nghe là người mới bắt đầu, hãy giải thích các thuật ngữ và đưa ra lời khuyên đơn giản, dễ thực hiện. "
            "Tránh các kỹ thuật phức tạp và tập trung vào những bước cơ bản."
        )
    elif experience_level == "advanced":
        return base_prompt + (
            " Người nghe có kinh nghiệm, hãy đưa ra lời khuyên chuyên sâu và các kỹ thuật nâng cao. "
            "Có thể sử dụng thuật ngữ chuyên môn và đề xuất các phương pháp chăm sóc tinh tế."
        )
    else:  # intermediate
        return base_prompt + (
            " Người nghe có kinh nghiệm trung bình, hãy cân bằng giữa lời khuyên cơ bản và nâng cao. "
            "Giải thích ngắn gọn các thuật ngữ và đưa ra lời khuyên thực tế."
        )


def _generate_basic_podcast(weather_info: Optional[str] = None) -> str:
    """Generate a basic podcast when context is not available."""

    weather_part = ""
    if weather_info:
        weather_part = f"Thời tiết hôm nay: {weather_info}. "

    basic_script = (
        f"Chào mừng bạn đến với podcast chăm sóc cây hôm nay! "
        f"{weather_part}"
        f"Hôm nay là ngày tuyệt vời để dành thời gian cho những người bạn xanh của bạn. "
        f"Hãy kiểm tra độ ẩm của đất, quan sát lá cây xem có dấu hiệu gì bất thường không. "
        f"Nếu trời nắng, đảm bảo cây không bị ánh nắng trực tiếp quá lâu. "
        f"Và đừng quên dành một chút thời gian để thưởng thức vẻ đẹp xanh tươi - "
        f"điều này không chỉ tốt cho cây mà còn tốt cho tâm hồn bạn nữa!"
    )

    return basic_script


def text_to_wav_bytes(text: str) -> bytes:
    """Convert text to WAV audio bytes using local TTS model."""
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform  # tensor [1, length]

    waveform = output.squeeze(0)  # [length]
    buffer = io.BytesIO()
    torchaudio.save(
        buffer, waveform.unsqueeze(0), model.config.sampling_rate, format="wav"
    )
    buffer.seek(0)
    return buffer.read()


def generate_dummy_data(user_id):
    """Legacy function - kept for backward compatibility."""
    plant_names = ["Cây vạn niên thanh", "Cây lưỡi hổ", "Cây hạnh phúc"]
    plants_str = ", ".join(plant_names)
    return UserData(address="Hà Nội", plants=plants_str, userName="Hoa")


async def synthesize_edge_tts(text: str, voice: str = "vi-VN-HoaiMyNeural") -> bytes:
    """Convert text to speech using Edge TTS and return WAV bytes."""
    buffer_mp3 = io.BytesIO()

    # Call TTS and stream to BytesIO
    communicate = edge_tts.Communicate(text=text, voice=voice)
    async for chunk in communicate.stream():
        if chunk.get("type") == "audio" and "data" in chunk:
            buffer_mp3.write(chunk["data"])

    # Read MP3 from buffer and convert to WAV
    buffer_mp3.seek(0)
    audio = AudioSegment.from_file(buffer_mp3, format="mp3")

    buffer_wav = io.BytesIO()
    audio.export(buffer_wav, format="wav")
    buffer_wav.seek(0)
    return buffer_wav.read()
