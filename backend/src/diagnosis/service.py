"""Service for plant diagnosis and troubleshooting."""

import asyncio
import base64
import io
import logging
from typing import Any, Dict, List, Optional

from PIL import Image

from src.diagnosis.constants import (
    PREVENTION_TIPS,
)
from src.diagnosis.exceptions import (
    DiagnosisGenerationException,
    ImageProcessingException,
)
from src.diagnosis.schemas import (
    DiagnoseRequest,
    DiagnoseResponse,
    PlantIssue,
    Remedy,
)
from src.integrations.openai_api.openai_api import get_openai_client

logger = logging.getLogger(__name__)


class DiagnosisService:
    """Service for diagnosing plant issues and providing remedies."""

    def __init__(self):
        """Initialize the diagnosis service."""
        self.openai_client = None

    async def diagnose_plant(self, request: DiagnoseRequest) -> DiagnoseResponse:
        """Diagnose plant issues from symptoms and/or images."""
        logger.info(
            f"Diagnosing plant with {len(request.images)} images and symptoms: {request.symptoms[:50] if request.symptoms else 'None'}"
        )

        try:
            # Step 1: Process images if provided
            image_analysis = None
            if request.images:
                image_analysis = await self._analyze_images(request.images)

            # Step 2: Parse and structure symptoms
            structured_symptoms = await self._parse_symptoms(request.symptoms)

            # Step 3: Get plant context if plant_id provided
            plant_context = None
            if request.plant_id:
                plant_context = await self._get_plant_context(str(request.plant_id))

            # Step 4: Generate diagnosis using AI
            diagnosis_result = await self._generate_diagnosis(
                image_analysis, structured_symptoms, plant_context, request
            )

            # Step 5: Find similar cases (mock implementation)
            similar_cases_count = await self._find_similar_cases(
                structured_symptoms, image_analysis
            )

            # Step 6: Calculate overall severity
            overall_severity = self._calculate_overall_severity(
                diagnosis_result["issues"]
            )

            # Step 7: Generate prevention tips
            prevention_tips = self._get_prevention_tips(diagnosis_result["issues"])

            return DiagnoseResponse(
                issues=diagnosis_result["issues"],
                remedies=diagnosis_result["remedies"],
                prevention=prevention_tips,
                similar_cases=similar_cases_count,
                severity=overall_severity,
                disclaimer=self._get_disclaimer(),
            )

        except Exception as e:
            logger.error(f"Diagnosis generation failed: {str(e)}")
            raise DiagnosisGenerationException(
                f"Failed to generate diagnosis: {str(e)}"
            )

    async def _analyze_images(self, images: List[str]) -> Dict[str, Any]:
        """Analyze plant images for visual symptoms using OpenAI Vision."""
        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client or not images:
            return {"analysis": "No image analysis available", "features": []}

        try:
            # Process first image (can be extended for multiple images)
            image_data = images[0]

            # Validate and process image
            processed_image = self._process_image(image_data)

            prompt = """
            You are an expert plant pathologist. Analyze this plant image and identify any visible issues, symptoms, or problems.

            Look for:
            - Leaf discoloration, spots, or patterns
            - Wilting, drooping, or structural issues
            - Pest presence or damage signs
            - Root problems (if visible)
            - Growth abnormalities
            - Environmental stress indicators

            Provide detailed observations in JSON format:
            {
                "visible_symptoms": ["list of specific symptoms seen"],
                "affected_areas": ["which parts of plant are affected"],
                "severity_indicators": ["signs that indicate how severe the problem is"],
                "possible_causes": ["likely causes based on visual evidence"],
                "confidence_level": "high/medium/low"
            }

            Be specific and detailed in your observations.
            """

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{processed_image}"
                                },
                            },
                        ],
                    }
                ],
                temperature=0.2,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            if content is None:
                raise DiagnosisGenerationException("Empty response from OpenAI Vision")

            return self._parse_image_analysis(content)

        except Exception as e:
            logger.warning(f"Image analysis failed: {str(e)}")
            return {
                "analysis": f"Image analysis unavailable: {str(e)[:100]}",
                "features": [],
            }

    def _process_image(self, image_data: str) -> str:
        """Process and validate image data."""
        try:
            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]

            # Decode and validate image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Resize if too large (max 1024x1024 for OpenAI)
            if image.width > 1024 or image.height > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Save back to base64
            output_buffer = io.BytesIO()
            image.save(output_buffer, format="JPEG", quality=85)
            return base64.b64encode(output_buffer.getvalue()).decode()

        except Exception as e:
            raise ImageProcessingException(f"Failed to process image: {str(e)}")

    def _parse_image_analysis(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI vision response into structured data."""
        try:
            import json

            # Extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                # Fallback to text analysis
                return {"analysis": content, "features": [], "confidence_level": "low"}

        except Exception:
            return {"analysis": content, "features": [], "confidence_level": "low"}

    async def _parse_symptoms(self, symptoms: Optional[str]) -> Dict[str, Any]:
        """Parse and structure symptom descriptions using AI."""
        if not symptoms:
            return {"structured": {}, "categories": []}

        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client:
            return {"structured": {"raw": symptoms}, "categories": ["general"]}

        try:
            prompt = f"""
            Parse these plant symptoms into structured categories:
            
            Symptoms: {symptoms}
            
            Extract and categorize into JSON format:
            {{
                "physical_symptoms": ["leaf yellowing", "brown spots", etc.],
                "behavioral_symptoms": ["wilting", "dropping leaves", etc.],
                "growth_issues": ["stunted growth", "no new growth", etc.],
                "environmental_factors": ["recent repotting", "moved location", etc.],
                "timeline": "when symptoms started or progression",
                "severity": "mild/moderate/severe",
                "affected_areas": ["leaves", "stems", "roots", etc.]
            }}
            
            Be specific and extract all relevant information.
            """

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800,
            )

            content = response.choices[0].message.content
            if content is None:
                raise DiagnosisGenerationException(
                    "Empty response from symptom parsing"
                )

            return self._parse_symptom_response(content)

        except Exception as e:
            logger.warning(f"Symptom parsing failed: {str(e)}")
            return {"structured": {"raw": symptoms}, "categories": ["general"]}

    def _parse_symptom_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response for symptom analysis."""
        try:
            import json

            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                return {"structured": json.loads(json_str), "categories": ["parsed"]}
            else:
                return {"structured": {"raw": content}, "categories": ["general"]}

        except Exception:
            return {"structured": {"raw": content}, "categories": ["general"]}

    async def _get_plant_context(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """Get plant context information from database."""
        # This would integrate with PlantService to get plant details
        # For now, return None as implementation depends on UUID handling
        return None

    async def _generate_diagnosis(
        self,
        image_analysis: Optional[Dict[str, Any]],
        structured_symptoms: Dict[str, Any],
        plant_context: Optional[Dict[str, Any]],
        request: DiagnoseRequest,
    ) -> Dict[str, Any]:
        """Generate comprehensive diagnosis using AI."""
        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client:
            # Return fallback diagnosis
            return self._get_fallback_diagnosis()

        try:
            prompt = self._build_diagnosis_prompt(
                image_analysis, structured_symptoms, plant_context, request
            )

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            if content is None:
                raise DiagnosisGenerationException(
                    "Empty response from diagnosis generation"
                )

            return self._parse_diagnosis_response(content)

        except Exception as e:
            logger.warning(f"AI diagnosis failed: {str(e)}")
            return self._get_fallback_diagnosis()

    def _build_diagnosis_prompt(
        self,
        image_analysis: Optional[Dict[str, Any]],
        structured_symptoms: Dict[str, Any],
        plant_context: Optional[Dict[str, Any]],
        request: DiagnoseRequest,
    ) -> str:
        """Build comprehensive prompt for diagnosis generation."""
        prompt = """
        You are an expert plant pathologist and diagnostician. Based on the following information, 
        provide a comprehensive diagnosis with specific issues and detailed remedies.

        """

        if image_analysis:
            prompt += (
                f"IMAGE ANALYSIS:\n{image_analysis.get('analysis', 'No analysis')}\n\n"
            )

        if structured_symptoms:
            prompt += f"SYMPTOMS:\n{structured_symptoms.get('structured', {})}\n\n"

        if plant_context:
            prompt += f"PLANT CONTEXT:\n{plant_context}\n\n"

        prompt += """
        DIAGNOSIS REQUIREMENTS:
        Provide your response in the following JSON format:
        {
            "issues": [
                {
                    "category": "environmental|pest|disease|nutritional|structural",
                    "name": "specific issue name",
                    "severity": "mild|moderate|severe|critical",
                    "probability": 0.85,
                    "root_cause": "detailed explanation of what causes this issue"
                }
            ],
            "remedies": [
                {
                    "title": "Action title",
                    "steps": ["specific step 1", "specific step 2"],
                    "timeline": "expected improvement timeframe",
                    "priority": 1,
                    "is_organic": true
                }
            ]
        }
        
        IMPORTANT GUIDELINES:
        - Prioritize most likely issues based on evidence
        - Provide specific, actionable remedy steps
        - Include both immediate and long-term solutions
        - Consider organic/natural remedies when possible
        - Be conservative with severity assessments
        - Include prevention in remedy steps
        """

        return prompt

    def _parse_diagnosis_response(self, content: str) -> Dict[str, Any]:
        """Parse AI diagnosis response into structured format."""
        try:
            import json

            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                parsed = json.loads(json_str)

                # Convert to Pydantic models
                issues = [
                    PlantIssue(
                        category=issue.get("category", "environmental"),
                        name=issue.get("name", "Unknown Issue"),
                        severity=issue.get("severity", "moderate"),
                        probability=issue.get("probability", 0.5),
                        root_cause=issue.get("root_cause", "Cause under investigation"),
                    )
                    for issue in parsed.get("issues", [])
                ]

                remedies = [
                    Remedy(
                        title=remedy.get("title", "General Care"),
                        steps=remedy.get("steps", []),
                        timeline=remedy.get("timeline", "Varies"),
                        priority=remedy.get("priority", 1),
                        is_organic=remedy.get("is_organic", True),
                    )
                    for remedy in parsed.get("remedies", [])
                ]

                return {"issues": issues, "remedies": remedies}
            else:
                raise ValueError("No valid JSON found in response")

        except Exception:
            return self._get_fallback_diagnosis()

    def _get_fallback_diagnosis(self) -> Dict[str, Any]:
        """Return fallback diagnosis when AI is unavailable."""
        issues = [
            PlantIssue(
                category="environmental",
                name="General Care Issue",
                severity="moderate",
                probability=0.6,
                root_cause="Multiple factors may be affecting plant health",
            )
        ]

        remedies = [
            Remedy(
                title="Basic Plant Care Review",
                steps=[
                    "Check soil moisture - water only when top inch is dry",
                    "Ensure adequate but not excessive light",
                    "Verify proper drainage in pot",
                    "Inspect for pests on leaves and stems",
                    "Consider recent changes in care or environment",
                ],
                timeline="Monitor for 1-2 weeks",
                priority=1,
                is_organic=True,
            )
        ]

        return {"issues": issues, "remedies": remedies}

    async def _find_similar_cases(
        self,
        structured_symptoms: Dict[str, Any],
        image_analysis: Optional[Dict[str, Any]],
    ) -> int:
        """Find similar diagnosis cases (mock implementation)."""
        # This would integrate with Pinecone vector database
        # to find similar cases based on symptoms and image features
        return 12  # Mock count

    def _calculate_overall_severity(self, issues: List[PlantIssue]) -> int:
        """Calculate overall severity score from individual issues."""
        if not issues:
            return 1

        severity_scores = {
            "mild": 1,
            "moderate": 2,
            "severe": 3,
            "critical": 4,
        }

        max_severity = max(severity_scores.get(issue.severity, 2) for issue in issues)

        return max_severity

    def _get_prevention_tips(self, issues: List[PlantIssue]) -> List[str]:
        """Generate prevention tips based on identified issues."""
        if not issues:
            return PREVENTION_TIPS["general"]

        prevention_tips = set()

        for issue in issues:
            category_tips = PREVENTION_TIPS.get(
                issue.category, PREVENTION_TIPS["general"]
            )
            prevention_tips.update(category_tips[:3])  # Add top 3 tips per category

        return list(prevention_tips)[:5]  # Return max 5 tips

    def _get_disclaimer(self) -> str:
        """Get standard diagnosis disclaimer."""
        return (
            "This AI-generated diagnosis is not a substitute for professional consultation. "
            "For severe issues, widespread problems, or concerns about plant safety around "
            "pets/children, please consult a qualified botanist or extension service."
        )
