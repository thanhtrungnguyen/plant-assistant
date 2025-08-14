"use server";

// Backend API response types
interface ActionStep {
  id: number;
  action: string;
}

interface PlantDiagnosisResponse {
  plant_name: string;
  condition: string;
  detail_diagnosis: string;
  action_plan: ActionStep[];
}

interface PlantDiagnosisError {
  error: string;
  message: string;
}

// Frontend error types
export interface AnalysisError {
  message: string;
  type: 'error';
}

// Frontend types (for compatibility)
export interface AnalysisResult {
  plantType: string;
  condition: string;
  diagnosis: string;
  treatments: ActionStep[];
}

// Union type for the actual response
export type AnalysisResponse = AnalysisResult | AnalysisError;

export async function analyzeImage(imageDataUrl: string): Promise<AnalysisResponse> {
  try {
    // Convert data URL to base64
    const base64Data = imageDataUrl.split(',')[1];

    // Convert base64 to blob for FormData
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/jpeg' });

    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', blob, 'plant-image.jpg');

    // Call backend API
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
    const response = await fetch(`${API_BASE_URL}/diagnose/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();

    // Check if result is an error
    if ('error' in result) {
      const errorResult = result as PlantDiagnosisError;

      // Transform backend error to frontend error format
      return transformBackendError(errorResult);
    }

    // Transform backend response to frontend format
    const diagnosisResult = result as PlantDiagnosisResponse;
    return transformBackendResponse(diagnosisResult);  } catch (error) {
    console.error('Error calling backend API:', error);

    // Re-throw the error instead of falling back to mock data
    throw error;
  }
}

function transformBackendResponse(backendResult: PlantDiagnosisResponse): AnalysisResult {
  return {
    plantType: backendResult.plant_name,
    condition: backendResult.condition,
    diagnosis: backendResult.detail_diagnosis,
    treatments: backendResult.action_plan,
  };
}

function transformBackendError(backendError: PlantDiagnosisError): AnalysisError {
  return {
    message: backendError.message,
    type: 'error',
  };
}
