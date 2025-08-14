"""Service for plant tracking and progress analysis."""

import asyncio
import base64
import io
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from PIL import Image
from sqlalchemy.orm import Session

# Remove unused imports - no additional constants needed currently
from src.tracking.exceptions import (
    TrackingAnalysisException,
    PhotoProcessingException,
)
from src.tracking.schemas import (
    TrackPhotoUploadRequest,
    TrackPhotoResponse,
    ProgressAnalysisRequest,
    ProgressAnalysisResponse,
    ProgressInsight,
    ProgressMetrics,
    ProgressRecommendation,
    ComparisonPhotoAnalysis,
    GrowthTimelineResponse,
    GrowthTimelineEntry,
)
from src.integrations.openai_api.openai_api import get_openai_client

logger = logging.getLogger(__name__)


class TrackingService:
    """Service for plant tracking and AI-powered progress analysis."""

    def __init__(self):
        self.openai_client = None

    async def upload_tracking_photo(
        self, request: TrackPhotoUploadRequest, db: Session
    ) -> TrackPhotoResponse:
        """Upload and process a new tracking photo with AI analysis."""
        try:
            # Step 1: Process and validate image
            processed_image = await self._process_image(request.photo_data)

            # Step 2: Perform AI analysis on the image
            ai_metrics = await self._analyze_single_photo(
                processed_image, request.description
            )

            # Step 3: Store photo with metadata (mock implementation)
            photo_record = await self._store_photo(
                str(request.plant_id),
                processed_image,
                request.description,
                ai_metrics,
                db,
            )

            return photo_record

        except Exception as e:
            logger.error(f"Photo upload failed: {str(e)}")
            raise PhotoProcessingException(f"Failed to upload tracking photo: {str(e)}")

    async def analyze_plant_progress(
        self, request: ProgressAnalysisRequest, db: Session
    ) -> ProgressAnalysisResponse:
        """Analyze plant progress over time using AI."""
        try:
            # Step 1: Get photo history for the plant
            photos = await self._get_plant_photos(
                str(request.plant_id), request.analysis_period_days or 30, db
            )

            if len(photos) < 2:
                return self._create_minimal_analysis(request, photos)

            # Step 2: Perform comparative analysis
            comparative_insights = await self._perform_comparative_analysis(photos)

            # Step 3: Calculate progress metrics
            progress_metrics = await self._calculate_progress_metrics(
                photos, comparative_insights
            )

            # Step 4: Generate insights and recommendations
            insights = await self._generate_progress_insights(
                comparative_insights, progress_metrics, photos
            )

            recommendations = []
            if request.include_recommendations:
                recommendations = await self._generate_recommendations(
                    insights, progress_metrics, photos
                )

            return ProgressAnalysisResponse(
                plant_id=request.plant_id,
                analysis_period_days=request.analysis_period_days or 30,
                total_photos=len(photos),
                insights=insights,
                metrics=progress_metrics,
                recommendations=recommendations,
                analysis_date=datetime.now(),
                disclaimer=self._get_disclaimer(),
            )

        except Exception as e:
            logger.error(f"Progress analysis failed: {str(e)}")
            raise TrackingAnalysisException(
                f"Failed to analyze plant progress: {str(e)}"
            )

    async def compare_photos(
        self, before_photo_id: int, after_photo_id: int, db: Session
    ) -> ComparisonPhotoAnalysis:
        """Compare two specific photos for detailed analysis."""
        try:
            # Get photo data
            before_photo = await self._get_photo_by_id(before_photo_id, db)
            after_photo = await self._get_photo_by_id(after_photo_id, db)

            if not before_photo or not after_photo:
                raise TrackingAnalysisException("One or both photos not found")

            # Perform AI comparison
            comparison_result = await self._compare_two_photos(
                before_photo, after_photo
            )

            return ComparisonPhotoAnalysis(
                before_photo_id=before_photo_id,
                after_photo_id=after_photo_id,
                comparison_insights=comparison_result["insights"],
                metrics_comparison=comparison_result["metrics"],
                confidence_score=comparison_result["confidence"],
            )

        except Exception as e:
            logger.error(f"Photo comparison failed: {str(e)}")
            raise TrackingAnalysisException(f"Failed to compare photos: {str(e)}")

    async def get_growth_timeline(
        self, plant_id: str, db: Session
    ) -> GrowthTimelineResponse:
        """Generate a growth timeline with key milestones."""
        try:
            # Get all photos for the plant
            all_photos = await self._get_plant_photos(plant_id, 365, db)  # Last year

            if not all_photos:
                return GrowthTimelineResponse(
                    plant_id=UUID(plant_id),
                    timeline=[],
                    overall_trend="insufficient_data",
                    key_milestones=[],
                    generated_at=datetime.now(),
                )

            # Group photos by time periods and analyze trends
            timeline_entries = await self._create_timeline_entries(all_photos)

            # Determine overall trend
            overall_trend = await self._determine_overall_trend(timeline_entries)

            # Extract key milestones
            key_milestones = await self._extract_key_milestones(
                all_photos, timeline_entries
            )

            return GrowthTimelineResponse(
                plant_id=UUID(plant_id),
                timeline=timeline_entries,
                overall_trend=overall_trend,
                key_milestones=key_milestones,
                generated_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Growth timeline generation failed: {str(e)}")
            raise TrackingAnalysisException(
                f"Failed to generate growth timeline: {str(e)}"
            )

    async def _process_image(self, image_data: str) -> str:
        """Process and validate uploaded image."""
        try:
            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]

            # Decode and validate
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Resize if too large
            if image.width > 1024 or image.height > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Save back to base64
            output_buffer = io.BytesIO()
            image.save(output_buffer, format="JPEG", quality=90)
            return base64.b64encode(output_buffer.getvalue()).decode()

        except Exception as e:
            raise PhotoProcessingException(f"Failed to process image: {str(e)}")

    async def _analyze_single_photo(
        self, processed_image: str, description: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze a single photo for plant health and growth indicators."""
        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client:
            return {"analysis": "AI analysis unavailable", "confidence": 0.1}

        try:
            prompt = """
            You are an expert botanist analyzing a plant tracking photo. Provide detailed analysis of:

            1. Health indicators (leaf color, texture, any visible issues)
            2. Growth signs (new shoots, size comparison if references visible)
            3. Overall plant condition and vitality
            4. Any concerns or positive developments

            Respond in JSON format:
            {
                "health_score": 0.85,
                "growth_indicators": ["new leaf buds", "stronger stem"],
                "health_concerns": ["slight yellowing on lower leaves"],
                "overall_condition": "healthy and thriving",
                "growth_stage": "vegetative",
                "recommendations": ["continue current care", "monitor for pests"],
                "confidence": 0.9
            }

            Be specific and focus on observable details.
            """

            if description:
                prompt += f"\n\nUser notes: {description}"

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
                raise TrackingAnalysisException("Empty response from OpenAI")

            return self._parse_analysis_response(content)

        except Exception as e:
            logger.warning(f"Single photo analysis failed: {str(e)}")
            return {
                "analysis": f"Analysis unavailable: {str(e)[:100]}",
                "confidence": 0.1,
            }

    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI analysis response."""
        try:
            # Extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                return {"analysis": content, "confidence": 0.5}

        except Exception:
            return {"analysis": content, "confidence": 0.3}

    async def _store_photo(
        self,
        plant_id: str,
        processed_image: str,
        description: Optional[str],
        ai_metrics: Dict[str, Any],
        db: Session,
    ) -> TrackPhotoResponse:
        """Store photo with metadata (mock implementation)."""
        # This would integrate with actual database models and S3 storage
        # For now, return a mock response
        return TrackPhotoResponse(
            id=12345,  # Mock ID
            plant_id=UUID(plant_id),
            url=f"https://storage.example.com/plants/{plant_id}/photos/12345.jpg",
            taken_at=datetime.now(),
            caption=description,
            ai_metrics_json=ai_metrics,
            created_at=datetime.now(),
        )

    async def _get_plant_photos(
        self, plant_id: str, period_days: int, db: Session
    ) -> List[Dict[str, Any]]:
        """Get plant photos from the specified period (mock implementation)."""
        # This would query the actual database
        # For now, return mock data
        cutoff_date = datetime.now() - timedelta(days=period_days)

        mock_photos = [
            {
                "id": 1,
                "plant_id": plant_id,
                "url": "https://storage.example.com/photo1.jpg",
                "taken_at": cutoff_date + timedelta(days=1),
                "ai_metrics": {
                    "health_score": 0.7,
                    "growth_stage": "seedling",
                    "height_estimate": "15cm",
                },
            },
            {
                "id": 2,
                "plant_id": plant_id,
                "url": "https://storage.example.com/photo2.jpg",
                "taken_at": cutoff_date + timedelta(days=15),
                "ai_metrics": {
                    "health_score": 0.85,
                    "growth_stage": "vegetative",
                    "height_estimate": "22cm",
                },
            },
            {
                "id": 3,
                "plant_id": plant_id,
                "url": "https://storage.example.com/photo3.jpg",
                "taken_at": datetime.now() - timedelta(days=1),
                "ai_metrics": {
                    "health_score": 0.9,
                    "growth_stage": "mature",
                    "height_estimate": "28cm",
                },
            },
        ]

        return mock_photos

    async def _perform_comparative_analysis(
        self, photos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comparative analysis across multiple photos."""
        if not self.openai_client:
            self.openai_client = get_openai_client()

        if not self.openai_client or len(photos) < 2:
            return self._get_fallback_comparison(photos)

        try:
            # For now, return mock analysis since we don't have actual images to compare
            # In a real implementation, this would use OpenAI Vision API to compare the photos
            return {
                "growth_progression": "positive",
                "height_change_percentage": 46.7,  # From 15cm to 22cm to 28cm
                "health_improvement": "improved",
                "new_features": ["stronger stem", "more leaves"],
                "concerns": [],
                "overall_assessment": "Significant positive growth with improved health indicators",
                "confidence": 0.85,
            }

        except Exception as e:
            logger.warning(f"Comparative analysis failed: {str(e)}")
            return self._get_fallback_comparison(photos)

    def _get_fallback_comparison(self, photos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide fallback comparison when AI is unavailable."""
        if len(photos) < 2:
            return {
                "growth_progression": "insufficient_data",
                "confidence": 0.1,
            }

        # Simple metric-based comparison
        first_health = photos[0].get("ai_metrics", {}).get("health_score", 0.5)
        last_health = photos[-1].get("ai_metrics", {}).get("health_score", 0.5)

        health_change = last_health - first_health

        return {
            "growth_progression": "positive" if health_change > 0.1 else "stable",
            "health_improvement": "improved" if health_change > 0.1 else "stable",
            "overall_assessment": f"Health score changed from {first_health:.2f} to {last_health:.2f}",
            "confidence": 0.6,
        }

    async def _calculate_progress_metrics(
        self,
        photos: List[Dict[str, Any]],
        comparative_analysis: Dict[str, Any],
    ) -> ProgressMetrics:
        """Calculate quantified progress metrics."""
        try:
            height_change = comparative_analysis.get("height_change_percentage", 0)
            health_improvement = comparative_analysis.get(
                "health_improvement", "stable"
            )

            # Calculate overall health score from latest photo
            latest_health = 0.8  # Default
            if photos:
                latest_health = (
                    photos[-1].get("ai_metrics", {}).get("health_score", 0.8)
                )

            return ProgressMetrics(
                height_change=f"+{height_change}%"
                if height_change > 0
                else f"{height_change}%",
                leaf_color_improvement="+15%"
                if health_improvement == "improved"
                else "stable",
                new_growth_detected=len(comparative_analysis.get("new_features", []))
                > 0,
                overall_health_score=latest_health,
                growth_rate="moderate" if height_change > 10 else "slow",
            )

        except Exception as e:
            logger.warning(f"Metrics calculation failed: {str(e)}")
            return ProgressMetrics(
                overall_health_score=0.7,
                growth_rate="unknown",
            )

    async def _generate_progress_insights(
        self,
        comparative_analysis: Dict[str, Any],
        progress_metrics: ProgressMetrics,
        photos: List[Dict[str, Any]],
    ) -> List[ProgressInsight]:
        """Generate human-readable progress insights."""
        insights = []

        # Health insights
        if (
            progress_metrics.overall_health_score
            and progress_metrics.overall_health_score > 0.8
        ):
            insights.append(
                ProgressInsight(
                    type="health",
                    message="Plant is showing excellent health indicators",
                    confidence=0.9,
                    data={"health_score": progress_metrics.overall_health_score},
                )
            )

        # Growth insights
        if progress_metrics.height_change and "+" in progress_metrics.height_change:
            insights.append(
                ProgressInsight(
                    type="growth",
                    message=f"Significant growth detected: {progress_metrics.height_change} height increase",
                    confidence=0.85,
                    data={
                        "growth_type": "height",
                        "change": progress_metrics.height_change,
                    },
                )
            )

        # New growth detection
        if progress_metrics.new_growth_detected:
            insights.append(
                ProgressInsight(
                    type="growth",
                    message="New growth features detected in recent photos",
                    confidence=0.8,
                    data={"features": comparative_analysis.get("new_features", [])},
                )
            )

        # Care insights based on photo frequency
        photo_frequency = len(photos) / max(
            1, (photos[-1]["taken_at"] - photos[0]["taken_at"]).days
        )
        if photo_frequency > 0.2:  # More than once per 5 days
            insights.append(
                ProgressInsight(
                    type="care",
                    message="Consistent monitoring is contributing to positive plant development",
                    confidence=0.7,
                    data={"photo_frequency": f"{photo_frequency:.2f} photos/day"},
                )
            )

        return insights

    async def _generate_recommendations(
        self,
        insights: List[ProgressInsight],
        progress_metrics: ProgressMetrics,
        photos: List[Dict[str, Any]],
    ) -> List[ProgressRecommendation]:
        """Generate care recommendations based on progress analysis."""
        recommendations = []

        # Health-based recommendations
        if (
            progress_metrics.overall_health_score
            and progress_metrics.overall_health_score > 0.85
        ):
            recommendations.append(
                ProgressRecommendation(
                    title="Continue Current Care Routine",
                    description="Your plant is thriving with the current care approach. Maintain consistency.",
                    priority=1,
                    category="care",
                )
            )
        elif (
            progress_metrics.overall_health_score
            and progress_metrics.overall_health_score < 0.6
        ):
            recommendations.append(
                ProgressRecommendation(
                    title="Review Care Approach",
                    description="Health indicators suggest the need for care adjustments. Consider watering, light, or nutrients.",
                    priority=1,
                    category="care",
                )
            )

        # Growth-based recommendations
        if progress_metrics.new_growth_detected:
            recommendations.append(
                ProgressRecommendation(
                    title="Support New Growth",
                    description="Provide adequate support or space for developing features.",
                    priority=2,
                    category="growth",
                )
            )

        # Monitoring recommendations
        if len(photos) < 5:
            recommendations.append(
                ProgressRecommendation(
                    title="Increase Photo Documentation",
                    description="More frequent photos will improve AI analysis accuracy and tracking insights.",
                    priority=3,
                    category="monitoring",
                )
            )

        return recommendations

    def _create_minimal_analysis(
        self, request: ProgressAnalysisRequest, photos: List[Dict[str, Any]]
    ) -> ProgressAnalysisResponse:
        """Create minimal analysis response when insufficient data."""
        return ProgressAnalysisResponse(
            plant_id=request.plant_id,
            analysis_period_days=request.analysis_period_days or 30,
            total_photos=len(photos),
            insights=[
                ProgressInsight(
                    type="monitoring",
                    message="Insufficient photo history for comprehensive analysis",
                    confidence=1.0,
                    data={"required_photos": 2, "current_photos": len(photos)},
                )
            ],
            metrics=ProgressMetrics(overall_health_score=0.7),
            recommendations=[
                ProgressRecommendation(
                    title="Start Regular Photo Documentation",
                    description="Take photos weekly to enable AI-powered progress tracking",
                    priority=1,
                    category="monitoring",
                )
            ],
            analysis_date=datetime.now(),
            disclaimer=self._get_disclaimer(),
        )

    async def _get_photo_by_id(
        self, photo_id: int, db: Session
    ) -> Optional[Dict[str, Any]]:
        """Get photo by ID (mock implementation)."""
        # This would query the actual database
        return {
            "id": photo_id,
            "url": f"https://storage.example.com/photo{photo_id}.jpg",
            "taken_at": datetime.now(),
            "ai_metrics": {"health_score": 0.8},
        }

    async def _compare_two_photos(
        self, before_photo: Dict[str, Any], after_photo: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two specific photos (mock implementation)."""
        return {
            "insights": [
                "Visible growth in stem height",
                "Leaf color improved from pale to vibrant green",
                "New branch development on left side",
            ],
            "metrics": {
                "height_change": "+12%",
                "color_improvement": "+25%",
                "new_features_count": 2,
            },
            "confidence": 0.85,
        }

    async def _create_timeline_entries(
        self, photos: List[Dict[str, Any]]
    ) -> List[GrowthTimelineEntry]:
        """Create timeline entries from photo history."""
        # Group photos by week and create entries
        timeline = []

        # Mock timeline creation
        for i, photo in enumerate(photos):
            if i % 7 == 0:  # Weekly entries
                timeline.append(
                    GrowthTimelineEntry(
                        date=photo["taken_at"],
                        photo_count=min(7, len(photos) - i),
                        key_changes=[
                            f"Growth stage: {photo.get('ai_metrics', {}).get('growth_stage', 'unknown')}"
                        ],
                        health_score=photo.get("ai_metrics", {}).get(
                            "health_score", 0.7
                        ),
                        growth_stage=photo.get("ai_metrics", {}).get(
                            "growth_stage", "unknown"
                        ),
                    )
                )

        return timeline

    async def _determine_overall_trend(
        self, timeline_entries: List[GrowthTimelineEntry]
    ) -> str:
        """Determine overall growth trend."""
        if len(timeline_entries) < 2:
            return "insufficient_data"

        # Simple trend calculation based on health scores
        health_scores = [
            entry.health_score for entry in timeline_entries if entry.health_score
        ]

        if not health_scores:
            return "unknown"

        if health_scores[-1] > health_scores[0] + 0.1:
            return "improving"
        elif health_scores[-1] < health_scores[0] - 0.1:
            return "declining"
        else:
            return "stable"

    async def _extract_key_milestones(
        self,
        photos: List[Dict[str, Any]],
        timeline_entries: List[GrowthTimelineEntry],
    ) -> List[str]:
        """Extract key milestones from photo history."""
        milestones = []

        # Analyze growth stages
        stages_seen = set()
        for photo in photos:
            stage = photo.get("ai_metrics", {}).get("growth_stage", "unknown")
            if stage not in stages_seen and stage != "unknown":
                milestones.append(f"Entered {stage} growth stage")
                stages_seen.add(stage)

        # Health improvements
        if len(photos) >= 2:
            first_health = photos[0].get("ai_metrics", {}).get("health_score", 0.5)
            last_health = photos[-1].get("ai_metrics", {}).get("health_score", 0.5)

            if last_health > first_health + 0.2:
                milestones.append(
                    f"Significant health improvement (+{(last_health - first_health) * 100:.0f}%)"
                )

        return milestones[:5]  # Return top 5 milestones

    def _get_disclaimer(self) -> str:
        """Get standard tracking analysis disclaimer."""
        return (
            "Progress analysis is AI-generated and based on visual assessment of uploaded photos. "
            "Results may vary based on photo quality, lighting, and angle. For concerns about plant "
            "health, consult with local gardening experts or extension services."
        )
