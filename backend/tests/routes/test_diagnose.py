"""
Tests for plant diagnosis API
"""
import pytest
from unittest.mock import patch, AsyncMock, Mock
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
import base64

from app.main import app
from app.services.plant_diagnosis import PlantDiagnosisService


client = TestClient(app)


def create_test_image() -> BytesIO:
    """Create a simple test image for testing"""
    image = Image.new('RGB', (200, 200), color='green')
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    return img_buffer


@pytest.mark.asyncio
class TestDiagnoseAPI:
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        with patch('app.services.plant_diagnosis.get_diagnosis_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/diagnose/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
    
    def test_diagnose_invalid_file_type(self):
        """Test diagnosis with invalid file type"""
        # Create a text file instead of image
        files = {"file": ("test.txt", "Hello world", "text/plain")}
        
        response = client.post("/diagnose/", files=files)
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    @patch('app.services.plant_diagnosis.get_diagnosis_service')
    async def test_diagnose_success(self, mock_get_service):
        """Test successful plant diagnosis"""
        # Mock the diagnosis service
        mock_service = AsyncMock()
        mock_service.diagnose_plant.return_value = {
            "plant_name": "Monstera Deliciosa",
            "condition": "Healthy", 
            "detail_diagnosis": "This plant shows excellent health with vibrant green leaves and proper growth patterns.",
            "action_plan": [
                {"id": 1, "action": "Continue current watering schedule"},
                {"id": 2, "action": "Maintain bright, indirect light"},
                {"id": 3, "action": "Monitor for pest activity monthly"}
            ]
        }
        mock_get_service.return_value = mock_service
        
        # Create test image
        img_buffer = create_test_image()
        files = {"file": ("plant.jpg", img_buffer, "image/jpeg")}
        
        response = client.post("/diagnose/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["plant_name"] == "Monstera Deliciosa"
        assert data["condition"] == "Healthy"
        assert len(data["action_plan"]) == 3
        assert data["action_plan"][0]["action"] == "Continue current watering schedule"
    
    @patch('app.services.plant_diagnosis.get_diagnosis_service')
    async def test_diagnose_service_error(self, mock_get_service):
        """Test diagnosis with service error"""
        # Mock service to return error
        mock_service = AsyncMock()
        mock_service.diagnose_plant.return_value = {
            "error": "validation_failed",
            "message": "Image does not contain a plant"
        }
        mock_get_service.return_value = mock_service
        
        # Create test image
        img_buffer = create_test_image()
        files = {"file": ("plant.jpg", img_buffer, "image/jpeg")}
        
        response = client.post("/diagnose/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["error"] == "validation_failed"
        assert "does not contain a plant" in data["message"]
    
    def test_diagnose_file_too_large(self):
        """Test diagnosis with oversized file"""
        # Create a large dummy file (simulate 11MB)
        large_content = b"0" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.jpg", large_content, "image/jpeg")}
        
        response = client.post("/diagnose/", files=files)
        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]


@pytest.mark.asyncio 
class TestPlantDiagnosisService:
    
    @patch('app.services.plant_diagnosis.settings')
    def test_service_initialization_without_api_key(self, mock_settings):
        """Test service fails without OpenAI API key"""
        mock_settings.OPENAI_API_KEY = None
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY not configured"):
            PlantDiagnosisService()
    
    @patch('app.services.plant_diagnosis.settings')
    @patch('app.services.plant_diagnosis.ChatOpenAI')
    def test_service_initialization_success(self, mock_chat_openai, mock_settings):
        """Test successful service initialization"""
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4o"
        mock_settings.OPENAI_VISION_MODEL = "gpt-4o"
        mock_settings.OPENAI_MAX_TOKENS = 1500
        mock_settings.OPENAI_TEMPERATURE = 0.1
        
        # Mock ChatOpenAI instances
        mock_llm = Mock()
        mock_vision_llm = Mock()
        mock_chat_openai.side_effect = [mock_llm, mock_vision_llm]
        
        service = PlantDiagnosisService()
        
        assert service.llm == mock_llm
        assert service.vision_llm == mock_vision_llm
        assert service.app is not None
