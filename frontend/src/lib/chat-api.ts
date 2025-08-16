/**
 * Chat API client for interacting with the plant assistant chatbot
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";

export interface ChatMessage {
  message: string;
  conversation_id?: string;
  plant_id?: number;
  image_data?: string; // Base64 encoded image
}

export interface ChatResponse {
  message_id: number;
  conversation_id: string;
  response: string;
  input_tokens: number;
  output_tokens: number;
  timestamp: string;
}

export interface Conversation {
  conversation_id: string;
  plant_id?: number;
  started_at: string;
  last_message?: string;
  last_message_time: string;
  source?: string;
  locale?: string;
}

export interface Message {
  message_id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  model?: string;
  token_prompt?: number;
  token_completion?: number;
  image_url?: string;
}

class ChatApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ChatApiError";
  }
}

class ChatApi {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}/api/chat${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include", // Include cookies for authentication
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ChatApiError(
        response.status,
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      );
    }

    return response.json();
  }

  /**
   * Send a message to the chatbot
   */
  async sendMessage(messageData: ChatMessage): Promise<ChatResponse> {
    return this.request<ChatResponse>("/message", {
      method: "POST",
      body: JSON.stringify(messageData),
    });
  }

  /**
   * Get all conversations for the current user
   */
  async getConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>("/conversations");
  }

  /**
   * Get messages for a specific conversation
   */
  async getConversationMessages(
    conversationId: string,
    limit = 50,
    offset = 0,
  ): Promise<Message[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });

    return this.request<Message[]>(`/conversations/${conversationId}/messages?${params}`);
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/conversations/${conversationId}`, {
      method: "DELETE",
    });
  }
}

export const chatApi = new ChatApi();
export { ChatApiError };
