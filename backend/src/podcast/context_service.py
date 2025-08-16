"""Podcast context service for retrieving and aggregating user context from Pinecone."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from src.core.config import settings
from src.chat.services.context_service import UserContextService
from .schemas import PodcastUserContext

logger = logging.getLogger(__name__)


class PodcastContextService:
    """Service for managing user context specifically for podcast generation."""

    def __init__(self):
        """Initialize the podcast context service."""
        self.user_context_service = UserContextService()
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=SecretStr(settings.OPENAI_API_KEY),
            temperature=0.1,
        )

    async def retrieve_podcast_context(
        self, user_id: int, location_context: Optional[str] = None, top_k: int = 3
    ) -> PodcastUserContext:
        """
        Retrieve and aggregate user context for podcast generation.

        Args:
            user_id: The user's ID
            location_context: Optional location/weather context for seasonal recommendations
            top_k: Number of context entries to retrieve (default 3)

        Returns:
            PodcastUserContext: Aggregated context optimized for podcast generation
        """
        try:
            # Use a comprehensive plant care query to get most relevant context
            context_query = self._build_context_query(location_context)
            logger.info(f"Using context query for user {user_id}: '{context_query}'")

            # Use podcast-specific retrieval that gets top 3 without threshold
            context_data = await self._retrieve_context_without_threshold(
                user_id=user_id, current_message=context_query, top_k=top_k
            )

            logger.info(
                f"Retrieved {len(context_data)} context entries for user {user_id}"
            )

            # Log summaries of found context for debugging
            for i, ctx in enumerate(context_data):
                summary = ctx.get("summary", "")[:100]
                score = ctx.get("relevance_score", 0)
                logger.info(f"Context {i + 1} (score: {score:.3f}): {summary}...")

            # Aggregate context into podcast-friendly format
            podcast_context = await self._aggregate_context_for_podcast(
                user_id=user_id,
                context_data=context_data,
                location_context=location_context,
            )

            return podcast_context

        except Exception as e:
            logger.error(f"Error retrieving podcast context for user {user_id}: {e}")
            # Return default context as fallback
            return self._get_default_context(user_id)

    async def _retrieve_context_without_threshold(
        self, user_id: int, current_message: str, top_k: int = 3
    ) -> List[Dict]:
        """
        Podcast-specific context retrieval that returns top k results without threshold filtering.
        This ensures we always get some context for podcast generation.
        """
        try:
            # Create embedding for current message
            query_embedding = await self.user_context_service.embeddings.aembed_query(
                current_message
            )

            # Import pinecone directly
            from src.database import pinecone

            # Query Pinecone for similar context without threshold filtering
            matches = pinecone.query_vector(
                embedding=query_embedding,
                top_k=top_k,
                filter={"user_id": user_id},
                namespace=self.user_context_service.context_namespace,
            )

            # Format results - return top k without any threshold filtering
            context_results = []
            for match in matches:
                if hasattr(
                    match, "score"
                ):  # Just verify score exists, no threshold check
                    metadata = getattr(match, "metadata", {})
                    context_results.append(
                        {
                            "relevance_score": match.score,
                            "conversation_id": metadata.get("conversation_id"),
                            "timestamp": metadata.get("timestamp"),
                            "summary": metadata.get("summary", ""),
                            "message_count": metadata.get("message_count", 0),
                            "context_type": metadata.get(
                                "context_type", "conversation_summary"
                            ),
                        }
                    )

            logger.info(
                f"Podcast context retrieval found {len(context_results)} entries for user {user_id} (top {top_k} without threshold)"
            )
            return context_results

        except Exception as e:
            logger.error(f"Error in podcast context retrieval for user {user_id}: {e}")
            return []

    def _build_context_query(self, location_context: Optional[str] = None) -> str:
        """Build a context query optimized for retrieving podcast-relevant information."""
        # Enhanced query terms that match how conversations are actually stored
        # Based on analysis of chat context storage patterns
        base_query = "cây trồng plant"

        if location_context:
            seasonal_terms = "thời tiết mùa nhiệt độ độ ẩm ánh sáng trong nhà ngoài trời seasonal care weather temperature humidity light indoor outdoor"
            return f"{base_query} {seasonal_terms} {location_context}"

        return base_query

    async def _aggregate_context_for_podcast(
        self,
        user_id: int,
        context_data: List[Dict],
        location_context: Optional[str] = None,
    ) -> PodcastUserContext:
        """Aggregate context data into a structured format for podcast generation."""
        try:
            # Initialize aggregated data
            plants_mentioned = []
            care_issues = []
            recommendations_given = []
            user_preferences = []
            experience_indicators = []
            recent_diagnoses = []

            # Process each context entry
            for context in context_data:
                summary = context.get("summary", "").lower()

                # Extract plant names (look for common patterns)
                plants_in_summary = self._extract_plant_names(summary)
                plants_mentioned.extend(plants_in_summary)

                # Extract care issues
                issues = self._extract_care_issues(summary)
                care_issues.extend(issues)

                # Extract recommendations
                recommendations = self._extract_recommendations(summary)
                recommendations_given.extend(recommendations)

                # Extract user preferences and experience level
                preferences = self._extract_user_preferences(summary)
                user_preferences.extend(preferences)

                # Extract experience level indicators
                experience = self._extract_experience_level(summary)
                if experience:
                    experience_indicators.append(experience)

                # Extract recent diagnoses if present
                diagnosis = self._extract_diagnosis_info(summary)
                if diagnosis:
                    recent_diagnoses.append(diagnosis)

            # Deduplicate and prioritize information (in English first)
            unique_plants = list(set(plants_mentioned))[
                :5
            ]  # Top 5 most mentioned plants
            unique_issues = list(set(care_issues))[:3]  # Top 3 common issues
            unique_recommendations = list(set(recommendations_given))[
                :3
            ]  # Top 3 recommendations
            unique_preferences = list(set(user_preferences))[:3]  # Top 3 preferences

            # Translate extracted context to Vietnamese using LLM
            translated_plants = await self._translate_to_vietnamese(
                unique_plants, "plant names"
            )
            translated_issues = await self._translate_to_vietnamese(
                unique_issues, "plant care issues"
            )
            translated_recommendations = await self._translate_to_vietnamese(
                unique_recommendations, "care recommendations"
            )
            translated_preferences = await self._translate_to_vietnamese(
                unique_preferences, "user preferences"
            )

            # Determine overall experience level
            experience_level = self._determine_experience_level(experience_indicators)

            # Log what we extracted for debugging
            logger.info(
                f"Extracted for user {user_id}: plants={translated_plants}, issues={translated_issues}, experience={experience_level}"
            )

            # Create structured context with Vietnamese translations
            return PodcastUserContext(
                user_id=user_id,
                plants_owned=translated_plants,
                common_care_issues=translated_issues,
                recent_recommendations=translated_recommendations,
                care_preferences=translated_preferences,
                experience_level=experience_level,
                recent_diagnoses=recent_diagnoses[:2],  # Most recent 2 diagnoses
                context_confidence=self._calculate_confidence_score(context_data),
                last_updated=datetime.utcnow().isoformat(),
            )

        except Exception as e:
            logger.error(f"Error aggregating context for user {user_id}: {e}")
            return self._get_default_context(user_id)

    async def _translate_to_vietnamese(
        self, items: List[str], context_type: str
    ) -> List[str]:
        """
        Translate a list of English items to Vietnamese using LLM.

        Args:
            items: List of English text items to translate
            context_type: Context description (e.g., "plant names", "care issues")

        Returns:
            List of Vietnamese translations
        """
        if not items:
            return []

        try:
            # Create translation prompt
            items_text = ", ".join(items)

            translation_prompt = f"""Please translate the following {context_type} from English to Vietnamese.
Provide ONLY the Vietnamese translations, separated by commas, in the same order as the input.
Keep plant names accurate and use common Vietnamese plant names when available.

English {context_type}: {items_text}

Vietnamese translations:"""

            # Use the existing LLM instance
            response = await self.llm.ainvoke(
                [{"role": "user", "content": translation_prompt}]
            )

            # Parse the response - access content properly from AIMessage
            if hasattr(response, "content") and isinstance(response.content, str):
                vietnamese_text = response.content.strip()
            else:
                vietnamese_text = str(response).strip()

            vietnamese_items = [item.strip() for item in vietnamese_text.split(",")]

            # Ensure we have the same number of items
            if len(vietnamese_items) == len(items):
                logger.info(
                    f"Successfully translated {len(items)} {context_type} to Vietnamese"
                )
                return vietnamese_items
            else:
                logger.warning(
                    f"Translation mismatch for {context_type}: expected {len(items)}, got {len(vietnamese_items)}"
                )
                # Pad or truncate to match original length
                if len(vietnamese_items) < len(items):
                    vietnamese_items.extend(
                        items[len(vietnamese_items) :]
                    )  # Keep original for missing translations
                else:
                    vietnamese_items = vietnamese_items[
                        : len(items)
                    ]  # Truncate if too many
                return vietnamese_items

        except Exception as e:
            logger.error(f"Error translating {context_type} to Vietnamese: {e}")
            # Return original items as fallback
            return items

    def _extract_plant_names(self, summary_text: str) -> List[str]:
        """Extract plant names from summary text. Context is in English, extract in English for LLM translation later."""
        # English plant names to look for in context (since context is stored in English)
        english_plant_names = [
            "pothos",
            "snake plant",
            "monstera",
            "fiddle leaf fig",
            "succulent",
            "cactus",
            "philodendron",
            "peace lily",
            "rubber plant",
            "spider plant",
            "zz plant",
            "aloe",
            "jade plant",
            "orchid",
            "fern",
            "bamboo",
            "dracaena",
            "croton",
            "calathea",
            "anthurium",
            "ficus",
            "ivy",
            "tomato",
            "eggplant",
            "pepper",
            "cucumber",
            "lettuce",
            "basil",
            "mint",
            "rosemary",
            "thyme",
            "lavender",
            "geranium",
            "begonia",
            "impatiens",
            "petunia",
            "marigold",
            "sunflower",
            "rose",
            "jasmine",
        ]

        found_plants = []
        summary_lower = summary_text.lower()

        # Look for English plant names in the context
        for plant in english_plant_names:
            if plant.lower() in summary_lower:
                # Skip generic terms
                if plant.lower() in ["plant", "tree", "houseplant"]:
                    continue
                found_plants.append(plant.title())

        # Return English names for later LLM translation
        return list(set(found_plants))  # Remove duplicates

    def _extract_care_issues(self, summary_text: str) -> List[str]:
        """Extract care issues mentioned in the summary. Context is in English, return English for LLM translation later."""
        # English issue keywords to look for in context
        issue_patterns = {
            "overwatering": [
                "overwater",
                "too much water",
                "root rot",
                "yellowing leaves",
                "soggy soil",
            ],
            "underwatering": [
                "underwater",
                "dry soil",
                "wilting",
                "crispy leaves",
                "dehydrated",
            ],
            "poor drainage": ["drainage", "waterlogged", "standing water", "soggy"],
            "lighting issues": ["light", "lighting", "sun", "shade", "bright", "dark"],
            "pest problems": [
                "pest",
                "spider mites",
                "aphids",
                "fungus gnats",
                "mealybugs",
                "scale",
            ],
            "nutrient deficiency": [
                "nutrient",
                "fertilizer",
                "deficiency",
                "pale leaves",
                "stunted growth",
            ],
            "humidity issues": ["humidity", "dry air", "brown tips", "crispy edges"],
            "temperature stress": ["temperature", "cold", "heat", "stress", "shock"],
            "fungal infection": [
                "fungal",
                "fungus",
                "mold",
                "powdery mildew",
                "black spot",
            ],
            "bacterial infection": [
                "bacterial",
                "bacteria",
                "soft rot",
                "bacterial blight",
            ],
        }

        found_issues = []
        summary_lower = summary_text.lower()

        for issue_key, keywords in issue_patterns.items():
            if any(keyword.lower() in summary_lower for keyword in keywords):
                # Return English name for LLM translation later
                found_issues.append(issue_key)

        return list(set(found_issues))  # Remove duplicates

    def _extract_recommendations(self, summary_text: str) -> List[str]:
        """Extract care recommendations from summary (English and Vietnamese)."""
        recommendations = []
        summary_lower = summary_text.lower()

        recommendation_patterns = {
            "Adjust watering schedule": ["watering", "tưới nước", "water", "nước"],
            "Consider repotting": ["repot", "thay chậu", "đổi chậu", "chậu mới"],
            "Review fertilization routine": [
                "fertiliz",
                "phân bón",
                "bón phân",
                "nutrient",
            ],
            "Relocate for better lighting": [
                (
                    "light" in summary_lower
                    and ("move" in summary_lower or "relocate" in summary_lower)
                ),
                "ánh sáng" in summary_lower
                and ("di chuyển" in summary_lower or "chuyển chỗ" in summary_lower),
            ],
            "Improve soil drainage": ["drainage", "thoát nước", "đất", "soil"],
            "Check for pests": ["pest", "sâu bệnh", "côn trùng", "bug"],
            "Increase humidity": ["humidity", "độ ẩm", "ẩm", "humid"],
            "Reduce watering frequency": ["reduce water", "giảm tưới", "ít nước hơn"],
        }

        for recommendation, patterns in recommendation_patterns.items():
            # Handle both string patterns and boolean expressions
            if any(
                (isinstance(pattern, bool) and pattern)
                or (isinstance(pattern, str) and pattern in summary_lower)
                for pattern in patterns
            ):
                recommendations.append(recommendation)

        return recommendations

    def _extract_user_preferences(self, summary_text: str) -> List[str]:
        """Extract user preferences from summary (English and Vietnamese)."""
        preferences = []
        summary_lower = summary_text.lower()

        preference_patterns = {
            "Prefers low-maintenance plants": [
                "low maintenance",
                "easy care",
                "dễ chăm sóc",
                "ít công sức",
                "không cần chăm nhiều",
            ],
            "Beginner-friendly options": [
                "beginner",
                "người mới",
                "mới bắt đầu",
                "dễ trồng",
            ],
            "Needs drought-tolerant plants": [
                "travel",
                "du lịch",
                "đi xa",
                "khô hạn",
                "chịu hạn",
            ],
            "Limited growing space": [
                "apartment",
                "small space",
                "chung cư",
                "không gian nhỏ",
                "diện tích hẹp",
            ],
            "Pet-safe plants required": [
                ("pet" in summary_lower and "safe" in summary_lower),
                "an toàn cho thú cưng",
                "không độc cho chó",
                "không độc cho mèo",
            ],
            "Prefers flowering plants": ["flower", "bloom", "hoa", "nở hoa", "ra hoa"],
            "Indoor growing preference": ["indoor", "trong nhà", "trong phòng"],
            "Outdoor gardening interest": [
                "outdoor",
                "garden",
                "ngoài trời",
                "sân vườn",
                "làm vườn",
            ],
        }

        for preference, patterns in preference_patterns.items():
            if any(
                (isinstance(pattern, bool) and pattern)
                or (isinstance(pattern, str) and pattern in summary_lower)
                for pattern in patterns
            ):
                preferences.append(preference)

        return preferences

    def _extract_experience_level(self, summary_text: str) -> Optional[str]:
        """Determine user experience level from summary (English and Vietnamese)."""
        summary_lower = summary_text.lower()

        # Beginner indicators
        beginner_terms = [
            "beginner",
            "new to plants",
            "first plant",
            "người mới",
            "mới bắt đầu",
            "lần đầu trồng",
            "chưa có kinh nghiệm",
            "không biết",
            "cần hướng dẫn",
        ]

        # Advanced indicators
        advanced_terms = [
            "experienced",
            "advanced",
            "có kinh nghiệm",
            "thành thạo",
            "chuyên nghiệp",
            "propagation",
            "nhân giống",
            "grafting",
            "ghép cành",
        ]

        # Intermediate indicators
        intermediate_terms = [
            "intermediate",
            "some experience",
            "trung bình",
            "một chút kinh nghiệm",
        ]

        if any(term in summary_lower for term in beginner_terms):
            return "beginner"
        elif any(term in summary_lower for term in advanced_terms):
            return "advanced"
        elif any(term in summary_lower for term in intermediate_terms):
            return "intermediate"

        return None

    def _extract_diagnosis_info(self, summary_text: str) -> Optional[Dict[str, str]]:
        """Extract diagnosis information if present (English and Vietnamese)."""
        summary_lower = summary_text.lower()

        diagnosis_terms = [
            "diagnos",
            "identified",
            "disease",
            "chẩn đoán",
            "xác định",
            "bệnh",
            "nhận dạng",
            "phân tích",
            "tình trạng",
            "triệu chứng",
            "symptom",
        ]

        if any(term in summary_lower for term in diagnosis_terms):
            has_vietnamese = any(
                term in summary_lower
                for term in [
                    "chẩn đoán",
                    "xác định",
                    "bệnh",
                    "nhận dạng",
                    "phân tích",
                    "tình trạng",
                    "triệu chứng",
                ]
            )
            return {
                "type": "health_diagnosis",
                "summary": summary_text[:200],  # First 200 chars as summary
                "language": "vietnamese" if has_vietnamese else "english",
            }
        return None

    def _determine_experience_level(self, experience_indicators: List[str]) -> str:
        """Determine overall experience level from multiple indicators."""
        if not experience_indicators:
            return "beginner"  # Default assumption

        # Count occurrences
        level_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for level in experience_indicators:
            level_counts[level] = level_counts.get(level, 0) + 1

        # Return most common level
        return max(level_counts.keys(), key=lambda x: level_counts[x])

    def _calculate_confidence_score(self, context_data: List[Dict]) -> float:
        """Calculate confidence score based on amount and quality of context data."""
        if not context_data:
            return 0.0

        # Base score on number of context entries and their relevance scores
        total_score = sum(ctx.get("relevance_score", 0) for ctx in context_data)
        avg_score = total_score / len(context_data)

        # Boost score based on number of entries (more context = higher confidence)
        volume_boost = min(len(context_data) * 0.1, 0.3)  # Max 30% boost

        return min(avg_score + volume_boost, 1.0)

    def _get_default_context(self, user_id: int) -> PodcastUserContext:
        """Return default context for users with no stored context."""
        logger.info(f"Using default context for user {user_id}")
        return PodcastUserContext(
            user_id=user_id,
            plants_owned=["houseplants"],  # Generic fallback
            common_care_issues=[],
            recent_recommendations=[],
            care_preferences=["beginner-friendly care"],
            experience_level="beginner",
            recent_diagnoses=[],
            context_confidence=0.0,
            last_updated=datetime.utcnow().isoformat(),
        )

    async def get_seasonal_recommendations(
        self,
        user_plants: List[str],
        weather_info: Optional[str] = None,
        season: Optional[str] = None,
    ) -> List[str]:
        """Generate seasonal care recommendations based on user's plants and weather (Vietnamese and English)."""
        recommendations = []

        # Default seasonal advice in Vietnamese (since podcast is in Vietnamese)
        if season or weather_info:
            recommendations.append(
                "Điều chỉnh tần suất tưới nước theo thay đổi của mùa"
            )
            recommendations.append("Theo dõi độ ẩm trong thời kỳ chuyển mùa")

        # Plant-specific seasonal advice in Vietnamese
        for plant in user_plants:
            plant_lower = plant.lower()

            # Vietnamese plant names
            if any(
                term in plant_lower
                for term in ["cây mọng nước", "xương rồng", "succulent", "cactus"]
            ):
                recommendations.append(
                    f"Giảm tưới nước cho {plant} trong những tháng lạnh hơn"
                )
            elif any(term in plant_lower for term in ["dương xỉ", "fern"]):
                recommendations.append(f"Tăng độ ẩm cho {plant} trong mùa khô")
            elif any(
                term in plant_lower for term in ["cây đàn hương", "fiddle leaf fig"]
            ):
                recommendations.append(f"Tránh di chuyển {plant} khi thay đổi nhiệt độ")
            elif any(term in plant_lower for term in ["cây cao su", "rubber plant"]):
                recommendations.append(f"Lau lá {plant} thường xuyên hơn trong mùa bụi")
            elif any(term in plant_lower for term in ["cây lưỡi hổ", "snake plant"]):
                recommendations.append(f"Giảm tưới nước cho {plant} vào mùa đông")
            elif any(term in plant_lower for term in ["cây trầu bà", "pothos"]):
                recommendations.append(f"Cắt tỉa {plant} để kích thích phát triển mới")

        return list(set(recommendations))  # Remove duplicates
