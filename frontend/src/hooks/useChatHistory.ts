"use client";

import { useEffect, useState } from "react";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  type: "text" | "image" | "analysis";
  imageUrl?: string;
  analysis?: any;
}

export interface ChatHistoryMessage {
  id: number;
  role: "user" | "assistant";
  content_text: string;
  image_url?: string;
  created_at: string;
}

export interface ConversationSession {
  id: number;
  started_at?: string;
  ended_at?: string;
  messages: ChatHistoryMessage[];
}

export interface ChatHistory {
  sessions: ConversationSession[];
  total_sessions: number;
}

export function useChatHistory() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      content:
        "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
      sender: "bot",
      timestamp: new Date(),
      type: "text",
    },
  ]);

  const [serverHistory, setServerHistory] = useState<ChatHistory | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Load messages from localStorage on component mount
  useEffect(() => {
    const savedMessages = localStorage.getItem("plant-assistant-chat");
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        // Convert timestamp strings back to Date objects
        const messagesWithDates = parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(messagesWithDates);
      } catch (error) {
        console.error("Error loading chat history:", error);
      }
    }
  }, []);

  // Save messages to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 1) {
      // Don't save if only welcome message
      localStorage.setItem("plant-assistant-chat", JSON.stringify(messages));
    }
  }, [messages]);

  // Fetch chat history from server
  const fetchServerHistory = async (limit: number = 10, offset: number = 0) => {
    setIsLoadingHistory(true);
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        console.log("No authentication token found");
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";
      const response = await fetch(
        `${apiUrl}/plants/chat/history?limit=${limit}&offset=${offset}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatHistory = await response.json();
      setServerHistory(data);
    } catch (error) {
      console.error("Error fetching chat history:", error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Convert server history messages to local format
  const convertServerHistoryToLocal = (history: ChatHistory): Message[] => {
    const convertedMessages: Message[] = [];

    // Add welcome message first
    convertedMessages.push({
      id: "welcome",
      content:
        "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
      sender: "bot",
      timestamp: new Date(),
      type: "text",
    });

    // Convert each session's messages
    history.sessions.forEach((session) => {
      session.messages.forEach((msg) => {
        convertedMessages.push({
          id: msg.id.toString(),
          content: msg.content_text,
          sender: msg.role === "user" ? "user" : "bot",
          timestamp: new Date(msg.created_at),
          type: msg.image_url ? "image" : "text",
          imageUrl: msg.image_url,
        });
      });
    });

    return convertedMessages;
  };

  const loadHistoryFromServer = async () => {
    await fetchServerHistory();
    if (serverHistory) {
      const convertedMessages = convertServerHistoryToLocal(serverHistory);
      setMessages(convertedMessages);
    }
  };

  const addMessage = (message: Message) => {
    setMessages((prev) => [...prev, message]);
  };

  const clearHistory = () => {
    const welcomeMessage = {
      id: "welcome",
      content:
        "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
      sender: "bot" as const,
      timestamp: new Date(),
      type: "text" as const,
    };
    setMessages([welcomeMessage]);
    localStorage.removeItem("plant-assistant-chat");
  };

  return {
    messages,
    addMessage,
    clearHistory,
    setMessages,
    serverHistory,
    isLoadingHistory,
    fetchServerHistory,
    loadHistoryFromServer,
  };
}

// Hook for plant care recommendations
export function usePlantRecommendations() {
  const [recommendations, setRecommendations] = useState<any[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("plant-recommendations");
    if (saved) {
      try {
        setRecommendations(JSON.parse(saved));
      } catch (error) {
        console.error("Error loading recommendations:", error);
      }
    }
  }, []);

  const addRecommendation = (recommendation: any) => {
    const newRecommendations = [
      ...recommendations,
      {
        ...recommendation,
        id: Date.now().toString(),
        timestamp: new Date(),
      },
    ];
    setRecommendations(newRecommendations);
    localStorage.setItem("plant-recommendations", JSON.stringify(newRecommendations));
  };

  const removeRecommendation = (id: string) => {
    const filtered = recommendations.filter((r) => r.id !== id);
    setRecommendations(filtered);
    localStorage.setItem("plant-recommendations", JSON.stringify(filtered));
  };

  return {
    recommendations,
    addRecommendation,
    removeRecommendation,
  };
}
