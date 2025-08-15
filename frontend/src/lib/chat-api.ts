/**
 * Chat API client for plant assistant chatbot
 */

export interface ChatMessage {
  id: number;
  session_id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  confidence_score?: number;
  tokens_used?: number;
  retrieved_context?: Array<{
    text: string;
    score: number;
    metadata: Record<string, any>;
  }>;
}

export interface ChatSession {
  id: number;
  user_id: number;
  title: string;
  is_active: boolean;
  created_at: string;
  last_activity: string;
  message_count: number;
  related_plant_ids?: number[];
}

export interface ChatSessionWithMessages extends ChatSession {
  messages: ChatMessage[];
}

export interface ChatRequest {
  message: string;
  session_id?: number;
  plant_id?: number;
  context?: string;
  use_rag?: boolean;
}

export interface ChatResponse {
  message: string;
  session_id: number;
  message_id: number;
  suggestions: string[];
  related_actions: string[];
  confidence: number;
  processing_time?: number;
  tokens_used?: number;
  retrieved_context?: Array<{
    text: string;
    score: number;
    metadata: Record<string, any>;
  }>;
}

export interface CreateSessionRequest {
  title?: string;
  user_preferences?: Record<string, any>;
  related_plant_ids?: number[];
}

class ChatApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:5000/api") {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    // Get auth token from localStorage or your auth system
    const token = typeof window !== "undefined" ? localStorage.getItem("authToken") : null;

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Send a chat message and get AI response
   */
  // Test endpoints
  async testConnection(): Promise<{status: string, message: string}> {
    return this.request('/chat/test');
  }

  async testMessage(message: string): Promise<any> {
    return this.request('/chat/test-message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  async testAIMessage(message: string): Promise<any> {
    return this.request('/chat/test-ai-message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // Main chat functionality
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>("/chat/", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  /**
   * Get user's chat sessions
   */
  async getSessions(activeOnly: boolean = true, limit: number = 50): Promise<ChatSession[]> {
    const params = new URLSearchParams({
      active_only: activeOnly.toString(),
      limit: limit.toString(),
    });

    return this.request<ChatSession[]>(`/chat/sessions?${params}`);
  }

  /**
   * Create a new chat session
   */
  async createSession(request: CreateSessionRequest): Promise<ChatSession> {
    return this.request<ChatSession>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  /**
   * Get a specific session with its messages
   */
  async getSessionWithMessages(
    sessionId: number,
    messageLimit?: number
  ): Promise<ChatSessionWithMessages> {
    const params = messageLimit
      ? new URLSearchParams({ message_limit: messageLimit.toString() })
      : new URLSearchParams();

    const queryString = params.toString();
    const endpoint = `/chat/sessions/${sessionId}${queryString ? `?${queryString}` : ""}`;

    return this.request<ChatSessionWithMessages>(endpoint);
  }

  /**
   * Update a chat session
   */
  async updateSession(
    sessionId: number,
    updates: {
      title?: string;
      is_active?: boolean;
      user_preferences?: Record<string, any>;
      related_plant_ids?: number[];
    }
  ): Promise<ChatSession> {
    return this.request<ChatSession>(`/chat/sessions/${sessionId}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId: number): Promise<void> {
    await this.request(`/chat/sessions/${sessionId}`, {
      method: "DELETE",
    });
  }

  /**
   * Get chat analytics
   */
  async getAnalytics(): Promise<{
    total_sessions: number;
    total_messages: number;
    active_sessions: number;
    avg_messages_per_session: number;
    avg_response_time: number;
    common_topics: Array<Record<string, any>>;
    user_satisfaction?: number;
  }> {
    return this.request("/chat/analytics");
  }

  /**
   * Health check for chat service
   */
  async healthCheck(): Promise<{
    status: string;
    service: string;
    features: string[];
  }> {
    return this.request("/chat/health");
  }
}

// Export singleton instance
export const chatApi = new ChatApiClient();
export default chatApi;
