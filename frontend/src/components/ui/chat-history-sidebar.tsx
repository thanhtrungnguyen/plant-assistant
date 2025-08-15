"use client";

import { Button } from "@/components/ui/button";
import { useChatHistory } from "@/hooks/useChatHistory";
import { Calendar, ChevronDown, ChevronUp, Clock, MessageCircle } from "lucide-react";
import { useEffect, useState } from "react";

interface ChatHistorySidebarProps {
  onLoadHistory: (messages: any[]) => void;
}

export function ChatHistorySidebar({ onLoadHistory }: ChatHistorySidebarProps) {
  const { serverHistory, isLoadingHistory, fetchServerHistory } = useChatHistory();
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedSession, setSelectedSession] = useState<number | null>(null);

  useEffect(() => {
    // Try to fetch history when component mounts
    fetchServerHistory().catch(() => {
      // Silently fail if not authenticated
    });
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const loadSessionMessages = (sessionId: number) => {
    if (!serverHistory) return;

    const session = serverHistory.sessions.find((s) => s.id === sessionId);
    if (!session) return;

    // Convert session messages to local format
    const messages = session.messages.map((msg) => ({
      id: msg.id.toString(),
      content: msg.content_text,
      sender: msg.role === "user" ? "user" : "bot",
      timestamp: new Date(msg.created_at),
      type: msg.image_url ? "image" : "text",
      imageUrl: msg.image_url,
    }));

    // Add welcome message at the beginning
    const welcomeMessage = {
      id: "welcome",
      content:
        "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
      sender: "bot" as const,
      timestamp: new Date(),
      type: "text" as const,
    };

    onLoadHistory([welcomeMessage, ...messages]);
    setSelectedSession(sessionId);
  };

  const getSessionPreview = (session: any) => {
    const firstUserMessage = session.messages.find((msg: any) => msg.role === "user");
    if (firstUserMessage) {
      return firstUserMessage.content_text.length > 40
        ? firstUserMessage.content_text.substring(0, 40) + "..."
        : firstUserMessage.content_text;
    }
    return "Cuộc trò chuyện mới";
  };

  // Show collapsed version if no history or loading failed
  if (isLoadingHistory || !serverHistory || serverHistory.sessions.length === 0) {
    return (
      <div className="bg-gray-50 border-r border-gray-200 p-3 w-80 flex-shrink-0">
        <div className="flex items-center gap-2 text-gray-600 text-sm">
          <MessageCircle className="h-4 w-4" />
          <span>{isLoadingHistory ? "Đang tải lịch sử..." : "Chưa có lịch sử"}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 border-r border-gray-200 flex flex-col w-80 flex-shrink-0">
      {/* Header */}
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full text-left hover:bg-gray-100 rounded p-2 transition-colors"
        >
          <div className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4 text-gray-600" />
            <span className="font-medium text-gray-900">
              Lịch sử ({serverHistory.total_sessions})
            </span>
          </div>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-500" />
          )}
        </button>
      </div>

      {/* History List */}
      {isExpanded && (
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {serverHistory.sessions.map((session) => (
            <div
              key={session.id}
              className={`p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-white cursor-pointer transition-colors ${
                selectedSession === session.id ? "border-blue-500 bg-white shadow-sm" : "bg-gray-50"
              }`}
              onClick={() => loadSessionMessages(session.id)}
            >
              <p className="text-sm font-medium text-gray-900 mb-1">{getSessionPreview(session)}</p>
              <div className="flex items-center gap-3 text-xs text-gray-500">
                {session.started_at && (
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(session.started_at)}</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <MessageCircle className="h-3 w-3" />
                  <span>{session.messages.length}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="p-3 border-t border-gray-200">
        <Button
          variant="outline"
          size="sm"
          onClick={() => fetchServerHistory()}
          disabled={isLoadingHistory}
          className="w-full"
        >
          <Clock className="h-4 w-4 mr-1" />
          Làm mới
        </Button>
      </div>
    </div>
  );
}
