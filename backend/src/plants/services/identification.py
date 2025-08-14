"""Plant identification service using AI models."""

import asyncio
import base64
import time
from io import BytesIO
from typing import Any, Dict, List, Optional

from PIL import Image

from src.integrations.openai_api.openai_api import get_openai_client
from src.plants.constants import (
    MAX_ALTERNATIVES,
    IdentificationConfidence,
)
from src.plants.exceptions import (
    IdentificationFailedException,
    InvalidImageFormatException,
)
from src.plants.schemas import IdentifyRequest, IdentifyResponse, PlantIdentification


class IdentificationService:
    """Service for plant identification using AI models."""

    def __init__(self):
        self.openai_client = None

    async def identify_plant(self, request: IdentifyRequest) -> IdentifyResponse:
        """Identify a plant from images and/or description."""
        start_time = time.time()

        try:
            # Process images if provided
            processed_images = []
            if request.images:
                processed_images = await self._process_images(request.images)

            # Perform identification using OpenAI Vision
            identification_result = await self._identify_with_openai(
                processed_images, request.description, request.user_metadata
            )

            # Get alternatives from vector database
            alternatives = await self._get_alternatives(identification_result)

            # Generate additional content
            fun_facts = await self._generate_fun_facts(identification_result)
            basic_info = self._generate_basic_info(identification_result)

            processing_time_ms = int((time.time() - start_time) * 1000)

            return IdentifyResponse(
                primary_identification=identification_result,
                alternatives=alternatives[:MAX_ALTERNATIVES],
                fun_facts=fun_facts,
                basic_info=basic_info,
                disclaimer=self._get_disclaimer(),
                processing_time_ms=processing_time_ms,
                confidence_level=self._get_confidence_level(
                    identification_result.confidence
                ),
            )

        except Exception as e:
            raise IdentificationFailedException(str(e))

    async def _process_images(self, base64_images: List[str]) -> List[str]:
        """Process and validate uploaded images."""
        processed = []

        for image_data in base64_images:
            try:
                # Decode base64
                image_bytes = base64.b64decode(image_data)

                # Open with PIL for processing
                with Image.open(BytesIO(image_bytes)) as img:
                    # Convert to RGB if needed
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    # Resize if too large (max 1024x1024)
                    if img.width > 1024 or img.height > 1024:
                        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

                    # Convert back to base64
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    processed_base64 = base64.b64encode(buffer.getvalue()).decode()
                    processed.append(processed_base64)

            except Exception as e:
                raise InvalidImageFormatException(f"Invalid image format: {str(e)}")

        return processed

    async def _identify_with_openai(
        self,
        images: List[str],
        description: Optional[str],
        metadata: Optional[Dict],
    ) -> PlantIdentification:
        """Use OpenAI Vision API for plant identification."""
        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client:
            raise IdentificationFailedException("OpenAI client not available")

        # Build the prompt
        prompt = self._build_identification_prompt(description, metadata)

        # Prepare messages
        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

        # Add images to the message
        for image_data in images:
            messages[0]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}",
                        "detail": "high",
                    },
                }
            )

        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=messages,  # type: ignore[arg-type]
                temperature=0.2,
                max_tokens=1000,
            )

            # Parse the response
            content = response.choices[0].message.content
            if content is None:
                raise IdentificationFailedException("Empty response from OpenAI API")
            return self._parse_openai_response(content)

        except Exception as e:
            raise IdentificationFailedException(f"OpenAI API error: {str(e)}")

    def _build_identification_prompt(
        self, description: Optional[str], metadata: Optional[Dict]
    ) -> str:
        """Build the prompt for plant identification."""
        prompt = """
        You are a botanical expert. Analyze the provided images and/or description to identify the plant.

        Provide a detailed identification including:
        1. Common name
        2. Scientific name (genus and species)
        3. Plant family
        4. Key identifying characteristics
        5. Native origin/habitat
        6. Growth habits and care requirements
        7. Confidence score (0.0 to 1.0)

        Format your response as JSON with these fields:
        {
            "common_name": "string",
            "scientific_name": "string",
            "family": "string",
            "genus": "string",
            "native_origin": "string",
            "key_traits": ["trait1", "trait2", ...],
            "growth_habits": "string",
            "confidence": 0.85
        }
        """

        if description:
            prompt += f"\n\nText description: {description}"

        if metadata:
            location = metadata.get("location")
            if location:
                prompt += f"\n\nLocation context: {location}"

        return prompt

    def _parse_openai_response(self, content: str) -> PlantIdentification:
        """Parse OpenAI response into PlantIdentification object."""
        try:
            import json

            # Try to extract JSON from the response
            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)

                return PlantIdentification(
                    common_name=data.get("common_name", "Unknown"),
                    scientific_name=data.get("scientific_name", "Unknown"),
                    family=data.get("family"),
                    genus=data.get("genus"),
                    native_origin=data.get("native_origin"),
                    key_traits=data.get("key_traits", []),
                    growth_habits=data.get("growth_habits"),
                    confidence=data.get("confidence", 0.5),
                )
            else:
                raise ValueError("No JSON found in response")

        except Exception:
            # Fallback parsing if JSON fails
            return PlantIdentification(
                common_name="Unknown Plant",
                scientific_name="Species unknown",
                confidence=0.1,
                key_traits=["AI parsing failed"],
            )

    async def _get_alternatives(
        self, primary: PlantIdentification
    ) -> List[PlantIdentification]:
        """Get alternative identifications from vector database."""
        # This would integrate with Pinecone for semantic search
        # For now, return empty list
        return []

    async def _generate_fun_facts(
        self, identification: PlantIdentification
    ) -> List[str]:
        """Generate fun facts about the identified plant."""
        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client:
            return ["Fun facts generation is temporarily unavailable."]

        try:
            prompt = f"""
            Generate 3-5 interesting and fun facts about {identification.common_name}
            ({identification.scientific_name}). Focus on:
            - Historical uses or cultural significance
            - Unique biological features
            - Surprising or little-known information
            - Etymology of the name

            Return as a simple list, one fact per line.
            """

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )

            content = response.choices[0].message.content
            if content is None:
                return ["Fun facts generation is temporarily unavailable."]

            facts = [fact.strip() for fact in content.split("\n") if fact.strip()]
            return facts[:5]  # Limit to 5 facts

        except Exception:
            return ["Fun facts generation is temporarily unavailable."]

    def _generate_basic_info(self, identification: PlantIdentification) -> str:
        """Generate basic introductory information."""
        if identification.growth_habits:
            return identification.growth_habits

        return f"{identification.common_name} is a plant in the {identification.family or 'unknown'} family."

    def _get_disclaimer(self) -> str:
        """Get the standard disclaimer text."""
        return (
            "This identification is AI-generated and may not be 100% accurate, "
            "especially for hybrids or rare variants. Always cross-verify with a "
            "botanist or extension service for edible, medicinal, or invasive species concerns."
        )

    def _get_confidence_level(self, confidence: float) -> IdentificationConfidence:
        """Convert numeric confidence to categorical level."""
        if confidence >= 0.91:
            return IdentificationConfidence.VERY_HIGH
        elif confidence >= 0.76:
            return IdentificationConfidence.HIGH
        elif confidence >= 0.51:
            return IdentificationConfidence.MEDIUM
        elif confidence >= 0.26:
            return IdentificationConfidence.LOW
        else:
            return IdentificationConfidence.VERY_LOW
