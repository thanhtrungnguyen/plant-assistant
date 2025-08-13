"""
Plant Diagnosis API Routes

Provides endpoint for plant health diagnosis using AI-powered image analysis.
"""

import base64
from typing import Union
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer

from app.schemas import PlantDiagnosisResponse, PlantDiagnosisError
from app.services.plant_diagnosis import PlantDiagnosisService, get_diagnosis_service


router = APIRouter(prefix="/diagnose", tags=["Plant Diagnosis"])
security = HTTPBearer()


@router.post(
    "/",
    response_model=Union[PlantDiagnosisResponse, PlantDiagnosisError],
    summary="Diagnose Plant Health",
    description="""
    Upload an image of a plant to receive AI-powered diagnosis including:
    - Plant species identification
    - Health condition assessment
    - Detailed diagnosis explanation  
    - Actionable treatment plan
    
    The image should be clear, well-lit, and show the plant's current condition.
    Supported formats: JPEG, PNG, WebP
    Maximum file size: 10MB
    """
)
async def diagnose_plant(
    file: UploadFile = File(..., description="Plant image file"),
    diagnosis_service: PlantDiagnosisService = Depends(get_diagnosis_service)
) -> Union[PlantDiagnosisResponse, PlantDiagnosisError]:
    """
    Diagnose plant health from uploaded image using multi-agent AI system.
    
    The diagnosis process involves multiple specialized AI agents:
    1. Input Validator - Ensures image contains a valid plant
    2. Plant Identifier - Identifies the plant species
    3. Condition Analyzer - Diagnoses health issues
    4. Action Plan Generator - Creates treatment recommendations
    5. Output Formatter - Structures the final response
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image file."
            )
        
        # Validate file size (10MB limit)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Convert to base64 for AI processing
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        # Process through multi-agent diagnosis system
        result = await diagnosis_service.diagnose_plant(image_base64)
        
        # Check if result is an error
        if "error" in result:
            return PlantDiagnosisError(**result)
        
        # Return successful diagnosis
        return PlantDiagnosisResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        return PlantDiagnosisError(
            error="processing_error",
            message=f"Failed to process plant diagnosis: {str(e)}"
        )
