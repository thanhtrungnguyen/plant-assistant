"""Plant diagnosis context service using Pinecone for context-based diagnosis."""

import logging
from datetime import datetime
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import SecretStr

from src.core.config import settings
from src.database.pinecone import query_vector, upsert_vectors
from .context_service import UserContextService

logger = logging.getLogger(__name__)


class PlantDiagnosisContextService:
    """Service for context-based plant diagnosis using Pinecone vector database."""

    def __init__(self):
        """Initialize the diagnosis context service."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=SecretStr(settings.OPENAI_API_KEY),
            temperature=0.1,
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDINGS_MODEL,
            api_key=SecretStr(settings.OPENAI_EMBEDDINGS_API_KEY),
        )
        self.user_context_service = UserContextService()
        self.diagnosis_namespace = "diagnosis_context"

    async def query_diagnosis_context(
        self, image_description: str, symptoms: str, user_id: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar diagnosis cases.

        Args:
            image_description: Description of the plant image
            symptoms: User-reported symptoms
            user_id: User identifier
            top_k: Number of similar cases to retrieve

        Returns:
            List of similar diagnosis cases from Pinecone
        """
        try:
            # Create search query combining image description and symptoms
            search_query = f"Plant diagnosis: {image_description}. Symptoms: {symptoms}"

            # Generate embeddings for the search query
            query_embedding = await self.embeddings.aembed_query(search_query)

            # Search Pinecone for similar diagnosis cases
            search_results = query_vector(
                embedding=query_embedding,
                top_k=top_k,
                namespace=self.diagnosis_namespace,
                filter=None,
            )

            context_results = []
            for match in search_results:
                if (
                    hasattr(match, "score") and match.score > 0.6
                ):  # Confidence threshold
                    metadata = getattr(match, "metadata", {})
                    context_data = {
                        "score": match.score,
                        "plant_name": metadata.get("plant_name", "Unknown"),
                        "condition": metadata.get("condition", "Unknown"),
                        "symptoms": metadata.get("symptoms", []),
                        "treatment": metadata.get("treatment", []),
                        "confidence": metadata.get("confidence", 0.0),
                        "image_description": metadata.get("image_description", ""),
                        "similar_cases": metadata.get("similar_cases", 0),
                    }
                    context_results.append(context_data)

            logger.info(
                f"Found {len(context_results)} similar diagnosis cases for user {user_id}"
            )
            return context_results

        except Exception as e:
            logger.error(f"Error querying diagnosis context: {e}")
            return []

    async def aggregate_diagnosis_context(
        self, context_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compile diagnosis from multiple Pinecone entries.

        Args:
            context_results: List of context results from Pinecone

        Returns:
            Aggregated diagnosis information
        """
        if not context_results:
            return {
                "plant_name": "Unknown",
                "condition": "Unable to determine",
                "confidence": 0.0,
                "treatments": [],
                "similar_cases_count": 0,
            }

        # Aggregate plant names and find most common
        plant_names = [ctx.get("plant_name", "Unknown") for ctx in context_results]
        most_common_plant = max(set(plant_names), key=plant_names.count)

        # Aggregate conditions and find most likely
        conditions = [
            ctx.get("condition", "Unknown")
            for ctx in context_results
            if ctx.get("condition") != "Unknown"
        ]
        most_likely_condition = (
            max(set(conditions), key=conditions.count) if conditions else "Healthy"
        )

        # Collect unique treatments
        all_treatments = []
        for ctx in context_results:
            treatments = ctx.get("treatment", [])
            if isinstance(treatments, list):
                all_treatments.extend(treatments)
            elif isinstance(treatments, str):
                all_treatments.append(treatments)

        unique_treatments = list(
            dict.fromkeys(all_treatments)
        )  # Remove duplicates while preserving order

        # Calculate overall confidence based on context scores
        total_confidence = sum(ctx.get("score", 0.0) for ctx in context_results)
        average_confidence = (
            total_confidence / len(context_results) if context_results else 0.0
        )

        return {
            "plant_name": most_common_plant,
            "condition": most_likely_condition,
            "confidence": average_confidence,
            "treatments": unique_treatments[:5],  # Top 5 treatments
            "similar_cases_count": len(context_results),
            "context_sources": context_results,
        }

    async def generate_context_diagnosis(
        self,
        aggregated_context: Dict[str, Any],
        user_preferences: Dict[str, Any],
        image_description: str = "",
        symptoms: str = "",
    ) -> str:
        """
        Generate diagnosis response from aggregated context.

        Args:
            aggregated_context: Compiled diagnosis information
            user_preferences: User context and preferences
            image_description: Original image description
            symptoms: User-reported symptoms

        Returns:
            Formatted diagnosis response
        """
        try:
            plant_name = aggregated_context.get("plant_name", "Unknown plant")
            condition = aggregated_context.get("condition", "Unknown")
            confidence = aggregated_context.get("confidence", 0.0)
            treatments = aggregated_context.get("treatments", [])
            similar_cases = aggregated_context.get("similar_cases_count", 0)

            # Get user experience level for response personalization
            experience_level = user_preferences.get("experience_level", "beginner")

            # Create personalized diagnosis prompt
            diagnosis_prompt = f"""
Based on similar plant diagnosis cases from our database, provide a diagnosis for this plant:

Plant: {plant_name}
Condition: {condition}
Confidence: {confidence:.2f}
Image Description: {image_description}
Symptoms: {symptoms}
Similar Cases Found: {similar_cases}
Available Treatments: {", ".join(treatments) if treatments else "None available"}

User Experience Level: {experience_level}

Generate a helpful diagnosis response that:
1. States the plant identification if confident (>0.7)
2. Describes the likely condition based on similar cases
3. Provides 2-3 actionable treatment recommendations appropriate for {experience_level} level
4. Mentions that this diagnosis is based on similar cases from our database
5. Includes confidence level and suggests when to seek additional help

Keep the response conversational, helpful, and appropriately detailed for the user's experience level.
"""

            response = await self.llm.ainvoke(diagnosis_prompt)
            response_content = (
                response.content if hasattr(response, "content") else str(response)
            )
            return (
                response_content.strip()
                if isinstance(response_content, str)
                else str(response_content)
            )

        except Exception as e:
            logger.error(f"Error generating context diagnosis: {e}")
            plant_name = aggregated_context.get("plant_name", "this plant")
            return f"Based on our database of similar cases, this appears to be a {plant_name}. However, I encountered an issue generating a detailed diagnosis. Please try uploading a clearer image or describe your plant's symptoms in more detail."

    async def store_diagnosis_context(
        self,
        user_id: str,
        plant_name: str,
        condition: str,
        symptoms: List[str],
        treatment: List[str],
        image_description: str,
        confidence: float = 0.8,
    ) -> bool:
        """
        Store new diagnosis context in Pinecone for future reference.

        Args:
            user_id: User identifier
            plant_name: Identified plant name
            condition: Plant health condition
            symptoms: List of symptoms observed
            treatment: List of treatment recommendations
            image_description: Description of the image
            confidence: Confidence score for the diagnosis

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create context text for embedding
            context_text = f"Plant: {plant_name}. Condition: {condition}. Symptoms: {', '.join(symptoms)}. Treatment: {', '.join(treatment)}. Description: {image_description}"

            # Generate embedding
            embedding = await self.embeddings.aembed_query(context_text)

            # Create metadata
            metadata = {
                "user_id": user_id,
                "context_type": "diagnosis",
                "plant_name": plant_name,
                "condition": condition,
                "symptoms": symptoms,
                "treatment": treatment,
                "confidence": confidence,
                "image_description": image_description,
                "timestamp": datetime.now().isoformat(),
                "similar_cases": 1,
            }

            # Generate unique ID
            vector_id = f"diagnosis_{user_id}_{datetime.now().timestamp()}"

            # Prepare vector for upsert
            vectors_to_upsert = [(vector_id, embedding, metadata)]

            # Upsert to Pinecone
            count = upsert_vectors(
                items=vectors_to_upsert, namespace=self.diagnosis_namespace
            )

            logger.info(f"Stored diagnosis context for user {user_id}: {plant_name}")
            return count > 0

        except Exception as e:
            logger.error(f"Error storing diagnosis context: {e}")
            return False

    async def get_fallback_diagnosis(
        self, image_description: str = "", symptoms: str = ""
    ) -> str:
        """
        Provide fallback diagnosis when insufficient context is available.

        Args:
            image_description: Description of the plant image
            symptoms: User-reported symptoms

        Returns:
            Fallback diagnosis response
        """
        fallback_message = "I don't have enough similar cases in our database to provide a confident diagnosis"

        if image_description:
            fallback_message += (
                f" for a plant with these characteristics: {image_description}"
            )

        if symptoms:
            fallback_message += f" showing these symptoms: {symptoms}"

        fallback_message += ". To get the best help:\n\n"
        fallback_message += "1. Try uploading a clearer, well-lit image of your plant\n"
        fallback_message += "2. Describe specific symptoms you've noticed (leaf color, spots, wilting, etc.)\n"
        fallback_message += (
            "3. Tell me about your care routine (watering, light, fertilizing)\n"
        )
        fallback_message += (
            "4. Mention how long you've had the plant and when symptoms started\n\n"
        )
        fallback_message += "With more information, I can provide better guidance based on similar cases from our community!"

        return fallback_message
