from openai import OpenAI
from typing import Optional

import requests
from ..core.config import settings
from fastapi.routing import APIRoute
import torch
from transformers import VitsModel, AutoTokenizer
import io
import torchaudio
import edge_tts
from .schemas import UserData
from pydub import AudioSegment

model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")


def simple_generate_unique_route_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# backend/src/app/utils.py


def get_weather(location_str: str) -> str:
    url = f"http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={location_str}&lang=vi"
    response = requests.get(url)
    data = response.json()
    condition = data["current"]["condition"]["text"]
    location_name = data["location"]["name"]
    temp = data["current"]["temp_c"]
    return f"Thời tiết hôm nay tại {location_name}: {condition}, nhiệt độ {temp}°C."


client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://aiportalapi.stu-platform.live/jpe",
)


def generate_podcast(name: str, plants: str, weather: Optional[str] = None) -> str:
    if weather:
        weather_part = f"- Thời tiết hôm nay: {weather}\n"
    else:
        weather_part = "- Không có thông tin thời tiết. Chỉ tập trung vào lời khuyên chăm sóc cây theo mùa hoặc chung chung.\n"

    prompt = (
        f"Hãy viết một đoạn podcast ngắn (khoảng 30 giây) dành cho {name}, bao gồm:\n"
        f"{weather_part}"
        f"- Danh sách cây trồng: {plants}\n"
        f"- Gợi ý những việc nên làm trong ngày để chăm sóc cây.\n"
        f"Văn phong nên truyền cảm hứng, nhẹ nhàng, gần gũi và khiến người nghe muốn kết nối với thiên nhiên và cây cối."
    )

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Bạn là một chuyên gia podcast về chăm sóc cây trồng. "
                    "Hãy tạo ra một đoạn podcast ngắn, truyền cảm hứng và hữu ích cho người yêu cây."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


def text_to_wav_bytes(text: str) -> bytes:
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
    plant_names = ["Cây vạn niên thanh", "Cây lưỡi hổ", "Cây hạnh phúc"]
    plants_str = ", ".join(plant_names)
    return UserData(address="Hà Nội", plants=plants_str, userName="Hoa")


async def synthesize_edge_tts(text: str, voice: str = "vi-VN-HoaiMyNeural") -> bytes:
    buffer_mp3 = io.BytesIO()

    # Gọi TTS và stream vào BytesIO
    communicate = edge_tts.Communicate(text=text, voice=voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer_mp3.write(chunk["data"])

    # Đọc MP3 từ buffer và chuyển sang WAV
    buffer_mp3.seek(0)
    audio = AudioSegment.from_file(buffer_mp3, format="mp3")

    buffer_wav = io.BytesIO()
    audio.export(buffer_wav, format="wav")
    buffer_wav.seek(0)
    return buffer_wav.read()
