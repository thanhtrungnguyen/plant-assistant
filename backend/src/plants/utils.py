"""Utility functions for the plants module."""

import base64
import uuid
from io import BytesIO
from typing import Optional

from PIL import Image

from .constants import (
    MAX_IMAGE_SIZE_MB,
    SUPPORTED_IMAGE_FORMATS,
)
from .exceptions import InvalidImageFormatException


def validate_image_format(content_type: str) -> bool:
    """Validate if the image format is supported."""
    if not content_type.startswith("image/"):
        return False

    format_name = content_type.split("/")[-1].lower()
    return format_name in SUPPORTED_IMAGE_FORMATS


def validate_image_size(
    image_data: bytes, max_size_mb: int = MAX_IMAGE_SIZE_MB
) -> bool:
    """Validate if the image size is within limits."""
    size_mb = len(image_data) / (1024 * 1024)
    return size_mb <= max_size_mb


def process_uploaded_image(
    image_data: bytes,
    max_width: int = 1024,
    max_height: int = 1024,
    quality: int = 85,
) -> bytes:
    """Process uploaded image: resize, compress, and optimize."""
    try:
        with Image.open(BytesIO(image_data)) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Save with optimization
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            return buffer.getvalue()

    except Exception as e:
        raise InvalidImageFormatException(f"Invalid image: {str(e)}")


def generate_filename(original_filename: str, user_id: int) -> str:
    """Generate a unique filename for uploaded images."""
    extension = (
        original_filename.split(".")[-1].lower() if "." in original_filename else "jpg"
    )
    unique_id = str(uuid.uuid4())
    return f"plant_photos/{user_id}/{unique_id}.{extension}"


def encode_image_to_base64(image_data: bytes) -> str:
    """Encode image data to base64 string."""
    return base64.b64encode(image_data).decode("utf-8")


def decode_base64_image(base64_string: str) -> bytes:
    """Decode base64 string to image data."""
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        raise InvalidImageFormatException(f"Invalid base64 data: {str(e)}")


def calculate_image_hash(image_data: bytes) -> str:
    """Calculate a hash for image deduplication."""
    import hashlib

    return hashlib.md5(image_data).hexdigest()


def extract_image_metadata(image_data: bytes) -> dict:
    """Extract metadata from image."""
    try:
        with Image.open(BytesIO(image_data)) as img:
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": len(image_data),
            }

            # Try to get EXIF data
            if hasattr(img, "getexif"):
                exif = img.getexif()
                if exif:
                    metadata["exif"] = dict(exif)

            return metadata

    except Exception:
        return {"error": "Could not extract metadata"}


def create_thumbnail(image_data: bytes, size: tuple = (150, 150)) -> bytes:
    """Create a thumbnail from image data."""
    try:
        with Image.open(BytesIO(image_data)) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            img.thumbnail(size, Image.Resampling.LANCZOS)

            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            return buffer.getvalue()

    except Exception as e:
        raise InvalidImageFormatException(f"Could not create thumbnail: {str(e)}")


def validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> bool:
    """Validate latitude and longitude coordinates."""
    if latitude is None and longitude is None:
        return True  # Both None is valid

    if latitude is None or longitude is None:
        return False  # One None, one not is invalid

    return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)


def format_plant_location(
    latitude: Optional[float], longitude: Optional[float]
) -> Optional[str]:
    """Format coordinates into a human-readable location string."""
    if (
        not validate_coordinates(latitude, longitude)
        or latitude is None
        or longitude is None
    ):
        return None

    lat_dir = "N" if latitude >= 0 else "S"
    lon_dir = "E" if longitude >= 0 else "W"

    return f"{abs(latitude):.6f}°{lat_dir}, {abs(longitude):.6f}°{lon_dir}"


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula."""
    import math

    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in kilometers
    r = 6371

    return c * r
