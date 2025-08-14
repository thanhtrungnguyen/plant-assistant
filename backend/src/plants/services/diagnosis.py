"""Service for plant diagnosis and troubleshooting."""

import logging

from src.plants.schemas.diagnosis import (
    DiagnoseRequest,
    DiagnoseResponse,
    PlantIssue,
    Remedy,
)

logger = logging.getLogger(__name__)


class DiagnosisService:
    """Service for diagnosing plant issues and providing remedies."""

    def __init__(self):
        """Initialize the diagnosis service."""
        pass

    async def diagnose_plant(self, request: DiagnoseRequest) -> DiagnoseResponse:
        """Diagnose plant issues from symptoms and/or images."""
        logger.info(
            f"Diagnosing plant with {len(request.images)} images and symptoms: {request.symptoms[:50] if request.symptoms else 'None'}"
        )

        # TODO: Implement LangGraph workflow:
        # 1. Parse inputs (OpenAI structured extraction for symptoms)
        # 2. Vision analysis (if images: OpenAI prompt for feature detection)
        # 3. Embed and query (Pinecone 'diagnosis_cases': search similar cases)
        # 4. Synthesize (OpenAI: diagnose and suggest remedies)

        # For now, return a basic diagnosis
        issues = [
            PlantIssue(
                category="environmental",
                name="Overwatering",
                severity="moderate",
                probability=0.75,
                root_cause="Excessive moisture leading to poor root health",
            ),
            PlantIssue(
                category="pest",
                name="Spider Mites",
                severity="mild",
                probability=0.25,
                root_cause="Low humidity and dry conditions",
            ),
        ]

        remedies = [
            Remedy(
                title="Adjust Watering Schedule",
                steps=[
                    "Check soil moisture by inserting finger 1-2 inches deep",
                    "Only water when top inch of soil feels dry",
                    "Ensure pot has proper drainage holes",
                    "Remove any standing water from saucer",
                ],
                timeline="Improvement expected in 7-10 days",
                priority=1,
                is_organic=True,
            ),
            Remedy(
                title="Increase Air Circulation",
                steps=[
                    "Move plant to area with better airflow",
                    "Use a small fan to improve circulation",
                    "Space plants apart to prevent crowding",
                    "Ensure room has adequate ventilation",
                ],
                timeline="Benefits visible within 3-5 days",
                priority=2,
                is_organic=True,
            ),
        ]

        prevention_tips = [
            "Use a moisture meter to monitor soil conditions accurately",
            "Sterilize pruning tools between plants to prevent disease spread",
            "Quarantine new plants for 2 weeks before introducing to collection",
            "Maintain consistent care schedule and monitor plants regularly",
            "Ensure proper plant spacing for adequate air circulation",
        ]

        return DiagnoseResponse(
            issues=issues,
            remedies=remedies,
            prevention=prevention_tips,
            similar_cases=12,
            severity=2,  # moderate overall
            disclaimer="This AI-generated diagnosis is not a substitute for professional consultation. For severe issues, widespread problems, or concerns about plant safety around pets/children, please consult a qualified botanist or extension service.",
        )
