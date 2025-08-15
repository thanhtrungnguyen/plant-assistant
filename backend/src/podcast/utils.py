from openai import OpenAI
import requests
from ..core.config import settings
from fastapi.routing import APIRoute
import torch
from transformers import VitsModel, AutoTokenizer
import io
import torchaudio
import torchaudio.transforms as T

# from app.services.viet_tts_utils.text import text_to_sequence
# from app.services.viet_tts_utils.vocoder import Vocoder
import numpy as np
import soundfile as sf
from .schemas import UserData

# am_sess = onnxruntime.InferenceSession("models/am_onnx/am_onnx.onnx")
# vocoder = Vocoder("models/mb_melgan.onnx")

# Sử dụng model TTS với giọng nữ tiếng Việt
# Có thể thay đổi model tùy theo yêu cầu chất lượng giọng nói
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
    api_key=openai_api_key,
    base_url="https://aiportalapi.stu-platform.live/jpe",
)


def generate_podcast(name: str, weather: str, plants: str) -> str:
    prompt = (
        f"Hãy viết một đoạn podcast ngắn khoảng 1-2 phút cho người dùng tên là {name}, bao gồm:\n"
        f"- Thời tiết hiện tại: {weather}\n"
        f"- Danh sách cây trồng: {plants}\n"
        f"- Gợi ý việc nên làm trong ngày để chăm sóc cây trồng dựa trên thời tiết.\n"
        f"- Lời khuyên chăm sóc cụ thể cho từng loại cây.\n"
        f"Văn phong truyền cảm hứng, thân thiện, khuyến khích người nghe tương tác với cây cối. "
        f"Giọng điệu như một người bạn quan tâm, nhiệt tình."
    )
    response = client.chat.completions.create(
        model="GPT-4o",
        messages=[
            {
                "role": "system",
                "content": "Bạn là một chuyên gia podcast về chăm sóc cây trồng, hãy tạo một podcast thú vị và hữu ích với giọng điệu thân thiện như một người bạn.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content  # type: ignore


def enhance_female_voice_soft(waveform: torch.Tensor, sample_rate: int) -> torch.Tensor:
    """
    Tạo giọng nữ nhẹ nhàng, dịu dàng
    """
    try:
        # Tăng pitch nhẹ (1-2 semitones)
        pitch_shift = T.PitchShift(sample_rate, n_steps=1.5)
        waveform_shifted = pitch_shift(waveform)
        
        # Chậm hơn để có cảm giác nhẹ nhàng
        speed_transform = T.Speed(sample_rate, factor=0.9)
        waveform_adjusted = speed_transform(waveform_shifted)
        
        # Lowpass filter mạnh hơn để có âm thanh mềm mại
        lowpass = T.LowpassBiquad(sample_rate, cutoff_freq=6000)
        waveform_filtered = lowpass(waveform_adjusted)
        
        # Giảm âm lượng để có cảm giác nhẹ nhàng
        max_val = torch.max(torch.abs(waveform_filtered))
        if max_val > 0:
            waveform_filtered = waveform_filtered / max_val * 0.7
        
        return waveform_filtered
    except Exception as e:
        print(f"Error in enhance_female_voice_soft: {e}")
        return waveform


def enhance_female_voice_energetic(waveform: torch.Tensor, sample_rate: int) -> torch.Tensor:
    """
    Tạo giọng nữ năng động, sôi nổi
    """
    try:
        # Tăng pitch cao hơn (3-4 semitones)
        pitch_shift = T.PitchShift(sample_rate, n_steps=4)
        waveform_shifted = pitch_shift(waveform)
        
        # Nhanh hơn để có cảm giác năng động
        speed_transform = T.Speed(sample_rate, factor=1.05)
        waveform_adjusted = speed_transform(waveform_shifted)
        
        # Tăng cường high frequencies để có âm thanh sáng hơn
        highpass = T.HighpassBiquad(sample_rate, cutoff_freq=200)
        waveform_filtered = highpass(waveform_adjusted)
        
        # Tăng âm lượng để có cảm giác năng động
        max_val = torch.max(torch.abs(waveform_filtered))
        if max_val > 0:
            waveform_filtered = waveform_filtered / max_val * 0.9
        
        return waveform_filtered
    except Exception as e:
        print(f"Error in enhance_female_voice_energetic: {e}")
        return waveform


def enhance_female_voice(waveform: torch.Tensor, sample_rate: int) -> torch.Tensor:
    """
    Tối ưu hóa giọng nói để có âm thanh giọng nữ tự nhiên hơn
    
    Args:
        waveform: Tensor âm thanh
        sample_rate: Tần số lấy mẫu
        
    Returns:
        torch.Tensor: Waveform đã được tối ưu
    """
    try:
        # Tăng pitch để có giọng nữ cao hơn (2-3 semitones)
        pitch_shift = T.PitchShift(sample_rate, n_steps=3)
        waveform_shifted = pitch_shift(waveform)
        
        # Làm mượt âm thanh bằng lowpass filter để giảm tạp âm
        lowpass = T.LowpassBiquad(sample_rate, cutoff_freq=8000)
        waveform_filtered = lowpass(waveform_shifted)
        
        # Điều chỉnh tốc độ nói để tự nhiên hơn (chậm hơn 5%)
        speed_transform = T.Speed(sample_rate, factor=0.95)
        waveform_adjusted = speed_transform(waveform_filtered)
        
        # Chuẩn hóa âm lượng
        max_val = torch.max(torch.abs(waveform_adjusted))
        if max_val > 0:
            waveform_adjusted = waveform_adjusted / max_val * 0.8  # Giảm 20% để tránh clipping
        
        return waveform_adjusted
    except Exception as e:
        print(f"Error in enhance_female_voice: {e}")
        # Fallback: chỉ điều chỉnh pitch đơn giản
        try:
            pitch_shift = T.PitchShift(sample_rate, n_steps=2)
            return pitch_shift(waveform)
        except:
            # Nếu tất cả đều thất bại, trả về waveform gốc
            return waveform


def text_to_wav_bytes(text: str, speaker_id: str = "female") -> bytes:
    """
    Chuyển đổi text thành audio với giọng nói được chỉ định
    
    Args:
        text: Văn bản cần chuyển đổi
        speaker_id: Loại giọng ("female", "male", "female_soft", "female_energetic")
    
    Returns:
        bytes: Dữ liệu âm thanh dạng WAV
    """
    inputs = tokenizer(text, return_tensors="pt")
    
    with torch.no_grad():
        # Tạo audio từ model
        output = model(**inputs).waveform
    
    waveform = output.squeeze(0)
    
    # Áp dụng điều chỉnh theo loại giọng
    if speaker_id in ["female", "female_soft", "female_energetic"]:
        if speaker_id == "female_soft":
            # Giọng nữ nhẹ nhàng: pitch thấp hơn, chậm hơn
            waveform = enhance_female_voice_soft(waveform.unsqueeze(0), model.config.sampling_rate).squeeze(0)
        elif speaker_id == "female_energetic":
            # Giọng nữ năng động: pitch cao hơn, nhanh hơn
            waveform = enhance_female_voice_energetic(waveform.unsqueeze(0), model.config.sampling_rate).squeeze(0)
        else:
            # Giọng nữ chuẩn
            waveform = enhance_female_voice(waveform.unsqueeze(0), model.config.sampling_rate).squeeze(0)
    
    sample_rate = model.config.sampling_rate
    
    buffer = io.BytesIO()
    torchaudio.save(
        buffer, 
        waveform.unsqueeze(0), 
        sample_rate, 
        format="wav"
    )
    buffer.seek(0)
    return buffer.read()


def generate_dummy_data(user_id):
    plant_names = ["Cây vạn niên thanh", "Cây lưỡi hổ", "Cây hạnh phúc"]
    plants_str = ", ".join(plant_names)
    return UserData(address="Hà Nội", plants=plants_str, userName="Minh")

    # def viet_tts_synthesize(text: str) -> bytes:
    seq = np.array([text_to_sequence(text)], dtype=np.int64)  # noqa: F821
    len_seq = np.array([len(seq[0])], dtype=np.int64)

    # Acoustic model (AM)
    ort_inputs = {"input_ids": seq, "input_lengths": len_seq}
    ort_outs = am_sess.run(None, ort_inputs)  # noqa: F821
    mel = ort_outs[0]

    # Vocoder
    wav = vocoder.infer(mel)[0]  # noqa: F821

    # Convert to bytes
    from io import BytesIO

    buffer = BytesIO()
    sf.write(buffer, wav, samplerate=22050, format="WAV")
    buffer.seek(0)
    return buffer.read()
