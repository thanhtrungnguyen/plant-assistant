/**
 * Chat API functions for Plant Care Assistant
 */

import { api } from "./api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  image_base64?: string;
  session_id?: string;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  session_id: string;
  timestamp: string;
  suggestions?: string[];
  plant_identified?: boolean;
  confidence_score?: number;
}

export interface ChatError {
  error: string;
  message: string;
  session_id?: string;
}

/**
 * Send a chat message to the plant care assistant
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse | ChatError> {
  try {
    // Use the simple chat endpoint that's available
    const response = await api("/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        error: "api_error",
        message: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        session_id: request.session_id,
      };
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("❌ Chat API error:", error);
    return {
      error: "network_error",
      message: "Không thể kết nối với server. Vui lòng thử lại.",
      session_id: request.session_id,
    };
  }
}

/**
 * Get chat session information
 */
export async function getChatSession(sessionId: string) {
  try {
    const response = await api(`/chat/sessions/${sessionId}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("❌ Get session error:", error);
    throw error;
  }
}

/**
 * Delete a chat session
 */
export async function deleteChatSession(sessionId: string) {
  try {
    const response = await api(`/chat/sessions/${sessionId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("❌ Delete session error:", error);
    throw error;
  }
}

/**
 * Convert file to base64 string for image upload
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
      if (typeof reader.result === "string") {
        // Remove data URL prefix (data:image/jpeg;base64,)
        const base64 = reader.result.split(",")[1];
        resolve(base64);
      } else {
        reject(new Error("Failed to convert file to base64"));
      }
    };

    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}
