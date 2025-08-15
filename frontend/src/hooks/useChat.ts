/**
 * Custom hook for chat functionality
 */

import { chatApi, ChatSession } from "@/lib/chat-api";
import { useCallback, useEffect, useRef, useState } from "react";

export interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  imageUrl?: string;
  confidence?: number;
  suggestions?: string[];
  relatedActions?: string[];
  retrievedContext?: Array<{
    text: string;
    score: number;
    metadata: Record<string, any>;
  }>;
}

export interface UseChatOptions {
  sessionId?: number;
  plantId?: number;
  useRag?: boolean;
  onError?: (error: Error) => void;
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Refs to track options
  const optionsRef = useRef(options);
  optionsRef.current = options;

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: "welcome",
        content: "Xin chào! Tôi là trợ lý AI chăm sóc cây trồng. Bạn có thể hỏi tôi về cách chăm sóc cây hoặc gửi ảnh cây để tôi phân tích.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    }
  }, [messages.length]);

  // Load existing session if sessionId provided
  useEffect(() => {
    if (options.sessionId && options.sessionId !== currentSession?.id) {
      loadSession(options.sessionId);
    }
  }, [options.sessionId]);

  const loadSession = useCallback(async (sessionId: number) => {
    try {
      setIsLoading(true);
      const sessionData = await chatApi.getSessionWithMessages(sessionId);
      setCurrentSession(sessionData);

      // Convert API messages to UI messages
      const uiMessages: Message[] = sessionData.messages.map((msg) => ({
        id: msg.id.toString(),
        content: msg.content,
        sender: msg.role === "user" ? "user" : "bot",
        timestamp: new Date(msg.created_at),
        confidence: msg.confidence_score,
        retrievedContext: msg.retrieved_context,
      }));

      setMessages(uiMessages);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to load session");
      setError(error.message);
      optionsRef.current.onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async (
    content: string,
    imageUrl?: string
  ): Promise<void> => {
    if ((!content.trim() && !imageUrl) || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: content.trim() || (imageUrl ? "Đã gửi ảnh cây trồng" : ""),
      sender: "user",
      timestamp: new Date(),
      imageUrl,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Use AI test API for intelligent responses
      const aiResponse = await chatApi.testAIMessage(content);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponse.response?.message || "Xin lỗi, tôi không thể trả lời lúc này.",
        sender: "bot",
        timestamp: new Date(),
        confidence: aiResponse.response?.confidence,
        suggestions: aiResponse.response?.suggestions,
        retrievedContext: aiResponse.response?.retrieved_context,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to send message");
      setError(error.message);
      optionsRef.current.onError?.(error);

      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
        sender: "bot",
        timestamp: new Date(),
        confidence: 0.1,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, currentSession]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentSession(null);
    setError(null);
  }, []);

  const createNewSession = useCallback(async (title?: string) => {
    try {
      const session = await chatApi.createSession({ title });
      setCurrentSession(session);
      clearMessages();
      return session;
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to create session");
      setError(error.message);
      optionsRef.current.onError?.(error);
      throw error;
    }
  }, [clearMessages]);

  return {
    messages,
    isLoading,
    currentSession,
    error,
    sendMessage,
    clearMessages,
    createNewSession,
    loadSession,
  };
}

// Hook for managing chat sessions list
export function useChatSessions() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSessions = useCallback(async (activeOnly: boolean = true) => {
    try {
      setIsLoading(true);
      setError(null);
      const sessionsData = await chatApi.getSessions(activeOnly);
      setSessions(sessionsData);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to load sessions");
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteSession = useCallback(async (sessionId: number) => {
    try {
      await chatApi.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to delete session");
      setError(error.message);
      throw error;
    }
  }, []);

  const updateSession = useCallback(async (
    sessionId: number,
    updates: { title?: string; is_active?: boolean }
  ) => {
    try {
      const updatedSession = await chatApi.updateSession(sessionId, updates);
      setSessions(prev => prev.map(s => s.id === sessionId ? updatedSession : s));
      return updatedSession;
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to update session");
      setError(error.message);
      throw error;
    }
  }, []);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    sessions,
    isLoading,
    error,
    loadSessions,
    deleteSession,
    updateSession,
  };
}
