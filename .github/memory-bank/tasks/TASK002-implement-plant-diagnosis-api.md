# [TASK002] - Implement Plant Diagnosis API with LangGraph Multi-Agent System

**Status:** In Progress  
**Added:** 2025-08-12  
**Updated:** 2025-08-12

## Original Request
Build the `/diagnose` API endpoint that takes an image as input and returns plant diagnosis using a LangGraph multi-agent system. The API should follow a specific workflow with specialized agents:

1. **Master Agent** - Orchestrates the entire workflow
2. **Input Validator** - Validates if image contains a valid plant
3. **Plant Identifier** - Identifies plant species
4. **Condition Analyzer** - Diagnoses plant health condition
5. **Action Plan Generator** - Creates treatment recommendations
6. **Output Formatter** - Formats final JSON response

Expected output format:
```json
{
  "plant_name": "[Plant Name]",
  "condition": "[Healthy or Disease Name]",
  "detail_diagnosis": "[Detailed Diagnosis Text]",
  "action_plan": [
    {"id": 1, "action": "[Action Step 1]"},
    {"id": 2, "action": "[Action Step 2]"}
  ]
}
```

## Thought Process
This is a core AI feature that differentiates the Plant Assistant application. The multi-agent approach provides several benefits:

1. **Separation of concerns**: Each agent has a specific responsibility
2. **Modularity**: Easy to modify individual agents without affecting others
3. **Error handling**: Failed validation stops the workflow early
4. **Scalability**: Can add more agents or modify workflow as needed
5. **State management**: LangGraph provides stateful workflow orchestration

Key design decisions:
- Use OpenAI Vision API for image analysis tasks (validation, identification, diagnosis)
- Use GPT-4o for text-based tasks (action plan generation)
- Implement comprehensive error handling at each stage
- Use FastAPI file upload for image handling with size and type validation
- Provide both success and error response schemas

## Implementation Plan
- ✅ Add required dependencies (OpenAI, LangGraph, LangChain, Pillow)
- ✅ Update configuration for OpenAI settings
- ✅ Create Pydantic schemas for request/response models
- ✅ Implement PlantDiagnosisService with LangGraph workflow
- ✅ Build multi-agent system with all 6 agents
- ✅ Create FastAPI route with file upload handling
- ✅ Add comprehensive error handling and validation
- ✅ Include the route in main FastAPI application
- ✅ Create unit tests for the API
- ✅ Test API server startup and documentation
- ⏳ Test with real OpenAI API key and sample images
- ⏳ Add integration tests with actual plant images
- ⏳ Performance optimization and error rate monitoring
- ⏳ Documentation and usage examples

## Progress Tracking

**Overall Status:** Near Complete - 85%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 2.1 | Add dependencies to pyproject.toml | Complete | 2025-08-12 | Added OpenAI, LangGraph, LangChain, Pillow |
| 2.2 | Update config with OpenAI settings | Complete | 2025-08-12 | Added API key and model configurations |
| 2.3 | Create Pydantic schemas | Complete | 2025-08-12 | PlantDiagnosisResponse and PlantDiagnosisError |
| 2.4 | Implement PlantDiagnosisService | Complete | 2025-08-12 | Full LangGraph workflow with 6 agents |
| 2.5 | Create FastAPI route | Complete | 2025-08-12 | /diagnose endpoint with file upload |
| 2.6 | Add route to main app | Complete | 2025-08-12 | Included diagnose_router in main.py |
| 2.7 | Create unit tests | Complete | 2025-08-12 | Test coverage for API and service |
| 2.8 | Test API startup | Complete | 2025-08-12 | Successfully starts on port 5001 |
| 2.9 | Real API testing | In Progress | 2025-08-12 | Need actual OpenAI key for testing |
| 2.10 | Integration testing | Not Started | 2025-08-12 | Test with variety of plant images |
| 2.11 | Performance optimization | Not Started | 2025-08-12 | Monitor response times and costs |

## Progress Log
### 2025-08-12
- Successfully added all required dependencies to pyproject.toml
- Updated configuration with OpenAI-specific settings and environment variables
- Created comprehensive Pydantic schemas for API request/response validation
- Implemented complete PlantDiagnosisService using LangGraph StateGraph
- Built multi-agent system with proper state management and error handling:
  - Input Validator: Validates image format and plant content using Vision API
  - Plant Identifier: Identifies species using Vision API with botanical expertise
  - Condition Analyzer: Diagnoses health condition with detailed analysis
  - Action Plan Generator: Creates structured treatment recommendations
  - Output Formatter: Ensures consistent JSON response format
  - Error Handler: Manages failures at any stage
- Created FastAPI route with comprehensive file upload validation (type, size limits)
- Added route to main FastAPI application and verified imports work
- Created unit tests covering API endpoints and service initialization
- Successfully started development server and verified API documentation
- API is functional and ready for testing with real OpenAI API key

**Next Steps:**
- Test with actual OpenAI API key using sample plant images
- Create integration tests with various plant conditions (healthy, diseased, pests)
- Monitor API performance and costs during testing
- Add response caching for repeated identical images
- Consider adding confidence scores for diagnosis reliability
