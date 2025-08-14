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
