"""Service for generating personalized plant care advice."""

import asyncio
import re
from typing import Any, Dict, List, Optional

from src.care.constants import (
    DEFAULT_CARE_INSTRUCTIONS,
    ECO_FRIENDLY_TIPS,
    SEASONAL_ADJUSTMENTS,
)
from src.care.exceptions import (
    CareAdviceGenerationException,
)
from src.care.schemas import CareRequest, CareResponse
from src.integrations.openai_api.openai_api import get_openai_client


class CareAdviceService:
    """Service for generating personalized plant care advice."""

    def __init__(self):
        self.openai_client = None

    async def generate_care_advice(self, request: CareRequest) -> CareResponse:
        """Generate comprehensive, personalized care advice."""
        try:
            # Step 1: Validate and process location
            location_data = await self._process_location(request.location)

            # Step 2: Get plant information if plant_id provided
            plant_info = None
            if request.plant_id:
                plant_info = await self._get_plant_info(str(request.plant_id))

            # Step 3: Generate base care plan using AI
            base_plan = await self._generate_base_care_plan(
                plant_info, location_data, request.environment, request.preferences
            )

            # Step 4: Add seasonal adjustments
            seasonal_adjustments = self._get_seasonal_adjustments(
                location_data, plant_info
            )

            # Step 5: Generate eco-friendly tips if requested
            eco_tips = self._get_eco_tips(request.preferences)

            # Step 6: Compile sources and disclaimer
            sources = self._get_sources()
            disclaimer = self._get_disclaimer()

            return CareResponse(
                plan=base_plan,
                seasonal_adjustments=seasonal_adjustments,
                eco_tips=eco_tips,
                sources=sources,
                disclaimer=disclaimer,
            )

        except Exception as e:
            raise CareAdviceGenerationException(
                f"Failed to generate care advice: {str(e)}"
            )

    async def _process_location(self, location: str) -> Dict[str, Any]:
        """Process location to determine climate zone and environmental factors."""
        # Check if location is a ZIP code (US)
        zip_match = re.match(r"^\d{5}(-\d{4})?$", location.strip())

        if zip_match:
            # Process US ZIP code to get USDA hardiness zone
            zip_code = zip_match.group(0)
            zone_data = await self._get_usda_zone(zip_code)
            return {
                "type": "zip_code",
                "value": zip_code,
                "hardiness_zone": zone_data.get("zone", "7a"),
                "climate_type": zone_data.get("climate", "temperate"),
                "avg_temp_range": zone_data.get("temp_range", "60-75°F"),
            }
        else:
            # Process general location (city, country, etc.)
            return {
                "type": "general",
                "value": location,
                "hardiness_zone": "7a",  # Default fallback
                "climate_type": "temperate",
                "avg_temp_range": "60-75°F",
            }

    async def _get_usda_zone(self, zip_code: str) -> Dict[str, Any]:
        """Get USDA hardiness zone data for a ZIP code."""
        # This would integrate with USDA API or cached data
        # For now, return mock data based on ZIP code patterns
        zip_int = int(zip_code[:3])

        if zip_int < 200:  # Northern states
            return {
                "zone": "4a-6b",
                "climate": "cold",
                "temp_range": "40-65°F",
            }
        elif zip_int < 600:  # Central states
            return {
                "zone": "6a-8a",
                "climate": "temperate",
                "temp_range": "50-75°F",
            }
        else:  # Southern states
            return {
                "zone": "8b-10a",
                "climate": "warm",
                "temp_range": "65-85°F",
            }

    async def _get_plant_info(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """Get plant information from database."""
        # This would use PlantService to get plant details
        # For now, return None as implementation depends on UUID handling
        return None

    async def _generate_base_care_plan(
        self,
        plant_info: Optional[Dict[str, Any]],
        location_data: Dict[str, Any],
        environment: Dict[str, Any],
        preferences: List[str],
    ) -> Dict[str, str]:
        """Generate base care plan using OpenAI."""
        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client:
            # Fallback to default care instructions
            return DEFAULT_CARE_INSTRUCTIONS.copy()

        try:
            # Build comprehensive prompt
            prompt = self._build_care_prompt(
                plant_info, location_data, environment, preferences
            )

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500,
            )

            content = response.choices[0].message.content
            if content is None:
                raise CareAdviceGenerationException("Empty response from OpenAI")

            # Parse response into structured care plan
            return self._parse_care_plan_response(content)

        except Exception as e:
            # Fallback to default instructions on error
            fallback_plan = DEFAULT_CARE_INSTRUCTIONS.copy()
            fallback_plan["note"] = (
                f"Using default care instructions due to: {str(e)[:100]}..."
            )
            return fallback_plan

    def _build_care_prompt(
        self,
        plant_info: Optional[Dict[str, Any]],
        location_data: Dict[str, Any],
        environment: Dict[str, Any],
        preferences: List[str],
    ) -> str:
        """Build detailed prompt for OpenAI care advice generation."""
        prompt = """
        You are an expert horticulturist and plant care advisor. Generate comprehensive, 
        personalized care instructions for a plant based on the following information.

        LOCATION CONTEXT:
        """

        prompt += f"- Location: {location_data['value']}\n"
        prompt += f"- Hardiness Zone: {location_data['hardiness_zone']}\n"
        prompt += f"- Climate: {location_data['climate_type']}\n"
        prompt += f"- Temperature Range: {location_data['avg_temp_range']}\n"

        prompt += "\nENVIRONMENT DETAILS:\n"
        for key, value in environment.items():
            prompt += f"- {key}: {value}\n"

        if preferences:
            prompt += "\nUSER PREFERENCES:\n"
            for pref in preferences:
                prompt += f"- {pref}\n"

        if plant_info:
            prompt += "\nPLANT INFORMATION:\n"
            for key, value in plant_info.items():
                prompt += f"- {key}: {value}\n"

        prompt += """
        
        INSTRUCTIONS:
        Provide detailed care instructions in the following categories. Be specific with:
        - Quantities (e.g., "8 oz of water")
        - Timing (e.g., "every 5-7 days")
        - Methods (e.g., "water until drainage appears")
        - Seasonal variations
        - Signs to watch for
        
        Format your response as JSON with these exact keys:
        {
            "watering": "detailed watering instructions",
            "light": "light requirements and positioning",
            "soil": "soil type, pH, drainage requirements",
            "humidity": "humidity needs and management",
            "temperature": "ideal temperature range and protection",
            "fertilizing": "fertilization schedule and types",
            "repotting": "when and how to repot",
            "pruning": "pruning techniques and timing",
            "special_notes": "any additional care considerations"
        }
        
        Prioritize organic methods if eco-friendly preferences are mentioned.
        Include metric/imperial conversions where applicable.
        """

        return prompt

    def _parse_care_plan_response(self, content: str) -> Dict[str, str]:
        """Parse OpenAI response into structured care plan."""
        try:
            import json

            # Extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                parsed_plan = json.loads(json_str)

                # Ensure all required keys are present
                required_keys = [
                    "watering",
                    "light",
                    "soil",
                    "humidity",
                    "temperature",
                    "fertilizing",
                    "repotting",
                    "pruning",
                ]

                for key in required_keys:
                    if key not in parsed_plan:
                        parsed_plan[key] = DEFAULT_CARE_INSTRUCTIONS.get(
                            key, "Instructions not available"
                        )

                return parsed_plan
            else:
                raise ValueError("No valid JSON found in response")

        except Exception:
            # Return default instructions if parsing fails
            return DEFAULT_CARE_INSTRUCTIONS.copy()

    def _get_seasonal_adjustments(
        self, location_data: Dict[str, Any], plant_info: Optional[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Generate seasonal care adjustments based on location and plant type."""
        climate = location_data.get("climate_type", "temperate")

        # Get base seasonal adjustments for climate
        adjustments = SEASONAL_ADJUSTMENTS.get(
            climate, SEASONAL_ADJUSTMENTS["temperate"]
        ).copy()

        # Add plant-specific adjustments if available
        if plant_info and "plant_type" in plant_info:
            plant_type = plant_info["plant_type"].lower()

            if "succulent" in plant_type or "cactus" in plant_type:
                adjustments["winter"].append("Reduce watering to once monthly")
                adjustments["winter"].append("Ensure temperature stays above 50°F")
            elif "tropical" in plant_type:
                adjustments["winter"].append("Increase humidity with humidifier")
                adjustments["winter"].append("Protect from cold drafts")

        return adjustments

    def _get_eco_tips(self, preferences: List[str]) -> List[str]:
        """Get eco-friendly care tips if user has eco preferences."""
        eco_prefs = ["organic", "eco-friendly", "sustainable", "green", "natural"]

        if any(pref.lower() in " ".join(preferences).lower() for pref in eco_prefs):
            return ECO_FRIENDLY_TIPS.copy()

        return []

    def _get_sources(self) -> List[str]:
        """Get reference sources for care recommendations."""
        return [
            "USDA Plant Hardiness Zone Map",
            "Royal Horticultural Society (RHS) Guidelines",
            "NASA Clean Air Study",
            "American Society for the Prevention of Cruelty to Animals (ASPCA)",
            "University Extension Services",
        ]

    def _get_disclaimer(self) -> str:
        """Get standard care advice disclaimer."""
        return (
            "Personalized based on provided inputs. Observe plant responses and adjust care accordingly. "
            "This advice is AI-generated and not a substitute for professional horticultural consultation. "
            "For edible, medicinal, or rare plants, consult with local extension services or certified botanists."
        )
