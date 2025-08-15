"""Command to seed plant knowledge into the RAG vector database."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

from src.chat.services.rag_service import RAGService
from src.core.logging import get_logger

logger = get_logger(__name__)


class PlantKnowledgeSeeder:
    """Seed plant knowledge into the RAG vector database."""

    def __init__(self):
        self.rag_service = RAGService()

    async def seed_basic_plant_knowledge(self) -> None:
        """Seed basic plant care knowledge."""

        basic_knowledge = [
            {
                "id": "watering_basics_001",
                "text": "Most houseplants should be watered when the top inch of soil feels dry to the touch. Overwatering is one of the most common causes of plant death. Check soil moisture by inserting your finger about 1 inch deep into the soil.",
                "category": "watering",
                "plant_type": "general",
                "difficulty_level": "beginner",
                "source": "plant_care_guide"
            },
            {
                "id": "light_requirements_001",
                "text": "Bright indirect light means the plant receives plenty of light but not direct sunlight. Place plants near a window with sheer curtains or a few feet away from a south-facing window. Direct sunlight can scorch most houseplant leaves.",
                "category": "lighting",
                "plant_type": "general",
                "difficulty_level": "beginner",
                "source": "plant_care_guide"
            },
            {
                "id": "fertilizing_basics_001",
                "text": "Most houseplants benefit from monthly fertilizing during spring and summer growing seasons. Use a balanced liquid fertilizer diluted to half strength. Avoid fertilizing in winter when plant growth slows down.",
                "category": "fertilizing",
                "plant_type": "general",
                "difficulty_level": "beginner",
                "source": "plant_care_guide"
            },
            {
                "id": "pothos_care_001",
                "text": "Pothos (Epipremnum aureum) is an excellent beginner plant. It tolerates low light and irregular watering. Water when soil is dry, provide bright indirect light, and trim long vines to encourage bushier growth. Yellow leaves usually indicate overwatering.",
                "category": "plant_specific_care",
                "plant_type": "pothos",
                "difficulty_level": "beginner",
                "source": "species_guide"
            },
            {
                "id": "snake_plant_care_001",
                "text": "Snake plants (Sansevieria) are extremely drought tolerant. Water every 2-3 weeks, allowing soil to dry completely between waterings. They can survive in low light but prefer bright, indirect light. Overwatering causes root rot.",
                "category": "plant_specific_care",
                "plant_type": "sansevieria",
                "difficulty_level": "beginner",
                "source": "species_guide"
            },
            {
                "id": "fiddle_leaf_care_001",
                "text": "Fiddle leaf figs (Ficus lyrata) need consistent care. They prefer bright, indirect light and should be watered when the top inch of soil is dry. Avoid moving them frequently as they don't like change. Brown spots often indicate watering issues.",
                "category": "plant_specific_care",
                "plant_type": "ficus",
                "difficulty_level": "intermediate",
                "source": "species_guide"
            },
            {
                "id": "pest_identification_001",
                "text": "Common houseplant pests include spider mites (tiny webs, stippled leaves), aphids (small green/black insects), and mealybugs (white cottony masses). Inspect plants regularly and isolate any infected plants immediately.",
                "category": "pest_control",
                "plant_type": "general",
                "difficulty_level": "intermediate",
                "source": "health_guide"
            },
            {
                "id": "repotting_basics_001",
                "text": "Repot plants when roots grow out of drainage holes or soil drains very quickly. Choose a pot only 1-2 inches larger in diameter. Use fresh potting mix and water thoroughly after repotting. Best time is spring before active growth.",
                "category": "repotting",
                "plant_type": "general",
                "difficulty_level": "intermediate",
                "source": "plant_care_guide"
            },
            {
                "id": "leaf_problems_001",
                "text": "Yellow leaves can indicate overwatering, underwatering, or natural aging. Brown leaf tips often mean low humidity or fluoride/chlorine in water. Dropping leaves may indicate stress from changes in light, temperature, or watering.",
                "category": "diagnosis",
                "plant_type": "general",
                "difficulty_level": "intermediate",
                "source": "health_guide"
            },
            {
                "id": "humidity_needs_001",
                "text": "Many houseplants benefit from 40-60% humidity. Increase humidity by grouping plants together, using a humidifier, or placing plants on pebble trays filled with water. Misting is less effective and can promote fungal issues.",
                "category": "environmental",
                "plant_type": "general",
                "difficulty_level": "beginner",
                "source": "plant_care_guide"
            }
        ]

        logger.info(f"Seeding {len(basic_knowledge)} basic knowledge items...")

        result = await self.rag_service.index_plant_knowledge(
            knowledge_items=basic_knowledge,
            namespace="plant_knowledge"
        )

        logger.info(f"Seeded basic knowledge: {result['successful']} successful, {result['failed']} failed")

    async def seed_care_specific_knowledge(self) -> None:
        """Seed care-specific knowledge."""

        care_knowledge = [
            {
                "id": "watering_frequency_001",
                "text": "Watering frequency depends on plant type, pot size, humidity, and season. Succulents need water every 1-2 weeks, tropicals every 1-2 weeks, and ferns may need water 2-3 times per week. Always check soil moisture first.",
                "category": "watering",
                "care_type": "watering_schedule",
                "plant_type": "general",
                "source": "care_schedule_guide"
            },
            {
                "id": "seasonal_care_001",
                "text": "Plant care changes with seasons. Spring and summer are growing seasons requiring more water and fertilizer. Fall and winter are dormant periods with reduced watering and no fertilizing for most plants.",
                "category": "seasonal_care",
                "season": "all",
                "plant_type": "general",
                "source": "seasonal_guide"
            },
            {
                "id": "propagation_basics_001",
                "text": "Many plants can be propagated from stem cuttings. Cut a 4-6 inch stem below a node, remove lower leaves, and place in water or moist soil. Roots typically develop in 2-4 weeks. Spring is the best time for propagation.",
                "category": "propagation",
                "plant_type": "general",
                "difficulty_level": "intermediate",
                "source": "propagation_guide"
            }
        ]

        logger.info(f"Seeding {len(care_knowledge)} care-specific knowledge items...")

        result = await self.rag_service.index_plant_knowledge(
            knowledge_items=care_knowledge,
            namespace="plant_care"
        )

        logger.info(f"Seeded care knowledge: {result['successful']} successful, {result['failed']} failed")

    async def seed_disease_knowledge(self) -> None:
        """Seed plant disease and problem knowledge."""

        disease_knowledge = [
            {
                "id": "root_rot_001",
                "text": "Root rot is caused by overwatering and poor drainage. Symptoms include yellowing leaves, soft black roots, and musty smell. Treatment: Remove plant from pot, trim black roots, repot in fresh well-draining soil, reduce watering.",
                "category": "diseases",
                "plant_type": "general",
                "symptoms": ["yellowing_leaves", "soft_roots", "musty_smell"],
                "source": "disease_guide"
            },
            {
                "id": "spider_mites_001",
                "text": "Spider mites appear as tiny moving dots with fine webbing on leaves. They cause stippled, yellowing leaves. Treatment: Increase humidity, spray with water, use insecticidal soap, or neem oil. Isolate infected plants.",
                "category": "pests",
                "plant_type": "general",
                "symptoms": ["webbing", "stippled_leaves", "tiny_insects"],
                "source": "pest_guide"
            },
            {
                "id": "nutrient_deficiency_001",
                "text": "Nutrient deficiencies show as yellowing leaves (nitrogen), purple/red leaves (phosphorus), or brown leaf edges (potassium). Solution: Use balanced fertilizer during growing season and ensure proper pH levels.",
                "category": "nutrition",
                "plant_type": "general",
                "symptoms": ["yellowing_leaves", "discolored_leaves", "brown_edges"],
                "source": "nutrition_guide"
            }
        ]

        logger.info(f"Seeding {len(disease_knowledge)} disease knowledge items...")

        result = await self.rag_service.index_plant_knowledge(
            knowledge_items=disease_knowledge,
            namespace="plant_diseases"
        )

        logger.info(f"Seeded disease knowledge: {result['successful']} successful, {result['failed']} failed")

    async def run_full_seed(self) -> None:
        """Run complete knowledge seeding."""
        logger.info("Starting plant knowledge seeding...")

        try:
            await self.seed_basic_plant_knowledge()
            await self.seed_care_specific_knowledge()
            await self.seed_disease_knowledge()

            # Get final stats
            stats = await self.rag_service.get_knowledge_stats()
            logger.info(f"Knowledge base seeding completed. Stats: {stats}")

        except Exception as e:
            logger.error(f"Knowledge seeding failed: {e}")
            raise


async def main():
    """Main entry point for seeding command."""
    seeder = PlantKnowledgeSeeder()
    await seeder.run_full_seed()


if __name__ == "__main__":
    asyncio.run(main())
