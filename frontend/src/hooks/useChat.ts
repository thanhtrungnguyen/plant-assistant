/**
 * Custom hook for managing chat functionality
 */

import { chatApi, ChatApiError, type ChatMessage, type ChatResponse, type Conversation } from '@/lib/chat-api';
import { useCallback, useEffect, useRef, useState } from 'react';

export interface ChatUIMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  imageUrl?: string;
  isLoading?: boolean;
}

export interface UseChatOptions {
  initialConversationId?: string;
  onError?: (error: ChatApiError) => void;
}

export function useChat(options: UseChatOptions = {}) {
  const { initialConversationId, onError } = options;

  const [messages, setMessages] = useState<ChatUIMessage[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(initialConversationId);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          content: 'Xin chào! Tôi là trợ lý AI chăm sóc cây trồng. Bạn có thể hỏi tôi về cách chăm sóc cây hoặc gửi ảnh cây để tôi phân tích.',
          sender: 'bot',
          timestamp: new Date(),
        },
      ]);
    }
  }, [messages.length]);

  const handleError = useCallback((error: ChatApiError) => {
    console.error('Chat API Error:', error);
    if (onError) {
      onError(error);
    } else {
      // Default error handling - add error message to chat
      const errorMessage: ChatUIMessage = {
        id: `error-${Date.now()}`,
        content: `Xin lỗi, đã có lỗi xảy ra: ${error.message}`,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev.map(msg => ({ ...msg, isLoading: false })), errorMessage]);
    }
  }, [onError]);

  const sendMessage = useCallback(async (
    content: string,
    imageData?: string,
    plantId?: number
  ) => {
    if ((!content.trim() && !imageData) || isLoading) return;

    const userMessage: ChatUIMessage = {
      id: `user-${Date.now()}`,
      content: content.trim() || (imageData ? 'Đã gửi ảnh cây trồng' : ''),
      sender: 'user',
      timestamp: new Date(),
      imageUrl: imageData,
    };

    // Add user message and loading indicator
    const loadingMessage: ChatUIMessage = {
      id: `loading-${Date.now()}`,
      content: '',
      sender: 'bot',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    try {
      const messageData: ChatMessage = {
        message: content,
        conversation_id: currentConversationId,
        plant_id: plantId,
        image_data: imageData,
      };

      const response: ChatResponse = await chatApi.sendMessage(messageData);

      // Update conversation ID if this is a new conversation
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
      }

      // Replace loading message with bot response
      setMessages(prev =>
        prev.filter(msg => !msg.isLoading).concat({
          id: `bot-${response.message_id}`,
          content: response.response,
          sender: 'bot',
          timestamp: new Date(response.timestamp),
        })
      );

    } catch (error) {
      handleError(error as ChatApiError);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, currentConversationId, handleError]);

  const loadConversations = useCallback(async () => {
    setIsLoadingConversations(true);
    try {
      const conversationList = await chatApi.getConversations();
      setConversations(conversationList);
    } catch (error) {
      handleError(error as ChatApiError);
    } finally {
      setIsLoadingConversations(false);
    }
  }, [handleError]);

  const loadConversation = useCallback(async (conversationId: string) => {
    setIsLoading(true);
    try {
      const messages = await chatApi.getConversationMessages(conversationId);

      // Convert API messages to UI messages
      const uiMessages: ChatUIMessage[] = messages.map(msg => ({
        id: msg.message_id,
        content: msg.content,
        sender: msg.role === 'user' ? 'user' : 'bot',
        timestamp: new Date(msg.timestamp),
        imageUrl: msg.image_url,
      }));

      setMessages(uiMessages);
      setCurrentConversationId(conversationId);
    } catch (error) {
      handleError(error as ChatApiError);
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  const startNewConversation = useCallback(() => {
    setCurrentConversationId(undefined);
    setMessages([
      {
        id: 'welcome-new',
        content: 'Xin chào! Tôi là trợ lý AI chăm sóc cây trồng. Bạn có thể hỏi tôi về cách chăm sóc cây hoặc gửi ảnh cây để tôi phân tích.',
        sender: 'bot',
        timestamp: new Date(),
      },
    ]);
  }, []);

  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      await chatApi.deleteConversation(conversationId);

      // Remove from conversations list
      setConversations(prev => prev.filter(conv => conv.conversation_id !== conversationId));

      // If this was the current conversation, start a new one
      if (currentConversationId === conversationId) {
        startNewConversation();
      }
    } catch (error) {
      handleError(error as ChatApiError);
    }
  }, [currentConversationId, startNewConversation, handleError]);

  return {
    messages,
    conversations,
    currentConversationId,
    isLoading,
    isLoadingConversations,
    messagesEndRef,
    sendMessage,
    loadConversations,
    loadConversation,
    startNewConversation,
    deleteConversation,
  };
}
