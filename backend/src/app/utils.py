from openai import OpenAI
import requests
from .config import settings
from fastapi.routing import APIRoute
from fastapi import APIRouter, Response, HTTPException
import torch
from transformers import VitsModel, AutoTokenizer
import io
import torchaudio
# from app.services.viet_tts_utils.text import text_to_sequence
# from app.services.viet_tts_utils.vocoder import Vocoder
import onnxruntime
import numpy as np
import soundfile as sf
from app.schemas import UserData

# am_sess = onnxruntime.InferenceSession("models/am_onnx/am_onnx.onnx")
# vocoder = Vocoder("models/mb_melgan.onnx")

model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")

def simple_generate_unique_route_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"
# backend/src/app/utils.py

def get_weather(location_str : str) -> str:
    url = f"http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={location_str}&lang=vi"
    response = requests.get(url)
    data = response.json()
    condition = data['current']['condition']['text']
    location_name = data["location"]["name"]
    temp = data['current']['temp_c']
    return f"Thời tiết hôm nay tại {location_name}: {condition}, nhiệt độ {temp}°C."


client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://aiportalapi.stu-platform.live/jpe"
)
def generate_podcast(name: str, weather: str, plants: str) -> str:
    prompt = (
        f"Hãy viết một đoạn podcast ngắn cho {name}, bao gồm:\n"
        f"- Thời tiết hiện tại: {weather}\n"
        f"- Danh sách cây trồng: {plants}\n"
        f"- Gợi ý việc nên làm trong ngày để chăm sóc cây trồng.\n"
        f"Văn phong truyền cảm hứng, thân thiện, khuyến khích người nghe tương tác với cây cối."
    )
    response = client.chat.completions.create(
        model="GPT-4o",
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia podcast về chăm sóc cây trồng, hãy tạo một podcast thú vị và hữu ích."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def text_to_wav_bytes(text: str) -> bytes:
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform  # tensor [1, length]

    waveform = output.squeeze(0)  # [length]
    buffer = io.BytesIO()
    torchaudio.save(buffer, waveform.unsqueeze(0), model.config.sampling_rate, format="wav")
    buffer.seek(0)
    return buffer.read()

def generate_dummy_data(user_id):
    plant_names = ['Cây vạn niên thanh', 'Cây lưỡi hổ', 'Cây hạnh phúc']
    plants_str = ', '.join(plant_names)
    return UserData(address = "Hà Nội" , plants = plants_str, userName = "Hoa")

# def viet_tts_synthesize(text: str) -> bytes:
    seq = np.array([text_to_sequence(text)], dtype=np.int64)
    len_seq = np.array([len(seq[0])], dtype=np.int64)

    # Acoustic model (AM)
    ort_inputs = {'input_ids': seq, 'input_lengths': len_seq}
    ort_outs = am_sess.run(None, ort_inputs)
    mel = ort_outs[0]

    # Vocoder
    wav = vocoder.infer(mel)[0]
    
    # Convert to bytes
    from io import BytesIO
    buffer = BytesIO()
    sf.write(buffer, wav, samplerate=22050, format='WAV')
    buffer.seek(0)
    return buffer.read()