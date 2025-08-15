"use client";

import { Button } from "@/components/ui/button";
import { useChatHistory } from "@/hooks/useChatHistory";
import { Calendar, Clock, History, Loader2, MessageCircle, Trash2, Users } from "lucide-react";
import { useEffect, useState } from "react";

interface ChatHistoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onLoadHistory: (messages: any[]) => void;
}

export function ChatHistoryPanel({ isOpen, onClose, onLoadHistory }: ChatHistoryPanelProps) {
  const [selectedSession, setSelectedSession] = useState<number | null>(null);
  
  // Demo data for testing
  const demoSessions = [
    {
      id: 1,
      started_at: new Date(Date.now() - 3600000).toISOString(),
      messages: [
        {
          id: 1,
          role: "user",
          content_text: "Xin chào! Tôi có một cây monstera và nó có vấn đề gì đó.",
          created_at: new Date(Date.now() - 3500000).toISOString(),
        },
        {
          id: 2,
          role: "assistant", 
          content_text: "Chào bạn! Tôi rất sẵn lòng giúp bạn với cây Monstera. Bạn có thể mô tả chi tiết vấn đề bạn đang gặp không?",
          created_at: new Date(Date.now() - 3400000).toISOString(),
        },
        {
          id: 3,
          role: "user",
          content_text: "Lá của nó bắt đầu vàng và có một số lá bị nâu ở mép.",
          created_at: new Date(Date.now() - 3300000).toISOString(),
        },
        {
          id: 4,
          role: "assistant",
          content_text: "Dựa vào mô tả của bạn, có thể cây đang gặp vấn đề về tưới nước. Lá vàng thường là dấu hiệu tưới quá nhiều hoặc thoát nước kém.",
          created_at: new Date(Date.now() - 3200000).toISOString(),
        },
      ]
    },
    {
      id: 2,
      started_at: new Date(Date.now() - 1800000).toISOString(),
      messages: [
        {
          id: 5,
          role: "user",
          content_text: "Tôi muốn hỏi về việc bón phân cho cây cảnh trong nhà.",
          created_at: new Date(Date.now() - 1700000).toISOString(),
        },
        {
          id: 6,
          role: "assistant",
          content_text: "Việc bón phân cho cây cảnh trong nhà rất quan trọng! Bạn đang trồng loại cây nào?",
          created_at: new Date(Date.now() - 1600000).toISOString(),
        },
        {
          id: 7,
          role: "user",
          content_text: "Tôi có cây pothos và cây snake plant.",
          created_at: new Date(Date.now() - 1500000).toISOString(),
        },
        {
          id: 8,
          role: "assistant",
          content_text: "Cả hai loại cây này đều rất dễ chăm sóc! Pothos thích phân bón cân bằng NPK, bón 1 lần/tháng vào mùa sinh trưởng.",
          created_at: new Date(Date.now() - 1400000).toISOString(),
        },
      ]
    },
    {
      id: 3,
      started_at: new Date(Date.now() - 300000).toISOString(),
      messages: [
        {
          id: 9,
          role: "user",
          content_text: "Cây của tôi có côn trùng nhỏ màu xanh trên lá, đó là gì?",
          created_at: new Date(Date.now() - 200000).toISOString(),
        },
        {
          id: 10,
          role: "assistant",
          content_text: "Nghe có vẻ như cây của bạn bị rệp xanh (aphids)! Đây là loại côn trùng hút nhựa cây rất phổ biến.",
          created_at: new Date(Date.now() - 100000).toISOString(),
        },
      ]
    }
  ];

  const serverHistory = {
    sessions: demoSessions,
    total_sessions: demoSessions.length
  };
  const isLoadingHistory = false;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const loadSessionMessages = (sessionId: number) => {
    if (!serverHistory) return;

    const session = serverHistory.sessions.find(s => s.id === sessionId);
    if (!session) return;

    // Convert session messages to local format
    const messages = session.messages.map(msg => ({
      id: msg.id.toString(),
      content: msg.content_text,
      sender: msg.role === "user" ? "user" : "bot",
      timestamp: new Date(msg.created_at),
      type: "text" as const,
      imageUrl: undefined,
    }));

    // Add welcome message at the beginning
    const welcomeMessage = {
      id: "welcome",
      content: "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
      sender: "bot" as const,
      timestamp: new Date(),
      type: "text" as const,
    };

    onLoadHistory([welcomeMessage, ...messages]);
    setSelectedSession(sessionId);
    onClose();
  };

  const getSessionPreview = (session: any) => {
    const firstUserMessage = session.messages.find((msg: any) => msg.role === "user");
    if (firstUserMessage) {
      return firstUserMessage.content_text.length > 50 
        ? firstUserMessage.content_text.substring(0, 50) + "..."
        : firstUserMessage.content_text;
    }
    return "Cuộc trò chuyện mới";
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Lịch sử trò chuyện</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ✕
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoadingHistory ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Đang tải lịch sử...</span>
            </div>
          ) : !serverHistory || serverHistory.sessions.length === 0 ? (
            <div className="text-center py-8">
              <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Chưa có lịch sử trò chuyện nào</p>
              <p className="text-sm text-gray-500 mt-2">
                Bắt đầu cuộc trò chuyện để lưu lại lịch sử
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                <Users className="h-4 w-4" />
                <span>Tổng cộng {serverHistory.total_sessions} cuộc trò chuyện</span>
              </div>

              {serverHistory.sessions.map((session) => (
                <div
                  key={session.id}
                  className={`p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors ${
                    selectedSession === session.id ? "border-blue-500 bg-blue-50" : ""
                  }`}
                  onClick={() => loadSessionMessages(session.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 mb-1">
                        {getSessionPreview(session)}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        {session.started_at && (
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span>{formatDate(session.started_at)}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <MessageCircle className="h-3 w-3" />
                          <span>{session.messages.length} tin nhắn</span>
                        </div>
                      </div>
                    </div>
                    <div className="ml-4">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                        Demo
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex justify-between items-center">
          <p className="text-xs text-gray-500">
            Đây là dữ liệu demo để trải nghiệm chức năng
          </p>
          <Button variant="outline" size="sm" onClick={onClose}>
            Đóng
          </Button>
        </div>
      </div>
    </div>
  );
}
