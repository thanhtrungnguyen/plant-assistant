"use client";

import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";
import { useEffect, useState } from "react";

interface DemoHistoryButtonProps {
  onLoadHistory: (messages: any[]) => void;
}

export function DemoHistoryButton({ onLoadHistory }: DemoHistoryButtonProps) {
  const [demoSessions] = useState([
    {
      id: 1,
      title: "Hỏi về cây Monstera bị vàng lá",
      messages: [
        {
          id: "demo-1",
          content:
            "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
          sender: "bot",
          timestamp: new Date(Date.now() - 3600000),
          type: "text",
        },
        {
          id: "demo-2",
          content: "Xin chào! Tôi có một cây monstera và nó có vấn đề gì đó.",
          sender: "user",
          timestamp: new Date(Date.now() - 3500000),
          type: "text",
        },
        {
          id: "demo-3",
          content:
            "Chào bạn! Tôi rất sẵn lòng giúp bạn với cây Monstera. Bạn có thể mô tả chi tiết vấn đề bạn đang gặp không? Ví dụ như lá có vàng, nâu hay có dấu hiệu bệnh nào khác?",
          sender: "bot",
          timestamp: new Date(Date.now() - 3400000),
          type: "text",
        },
        {
          id: "demo-4",
          content: "Lá của nó bắt đầu vàng và có một số lá bị nâu ở mép.",
          sender: "user",
          timestamp: new Date(Date.now() - 3300000),
          type: "text",
        },
        {
          id: "demo-5",
          content:
            "Dựa vào mô tả của bạn, có thể cây đang gặp vấn đề về tưới nước. Lá vàng thường là dấu hiệu tưới quá nhiều hoặc thoát nước kém. Bạn có thể kiểm tra độ ẩm của đất và đảm bảo chậu có lỗ thoát nước tốt không?",
          sender: "bot",
          timestamp: new Date(Date.now() - 3200000),
          type: "text",
        },
      ],
    },
    {
      id: 2,
      title: "Hỏi về bón phân cho cây cảnh",
      messages: [
        {
          id: "demo-6",
          content:
            "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
          sender: "bot",
          timestamp: new Date(Date.now() - 1800000),
          type: "text",
        },
        {
          id: "demo-7",
          content: "Tôi muốn hỏi về việc bón phân cho cây cảnh trong nhà.",
          sender: "user",
          timestamp: new Date(Date.now() - 1700000),
          type: "text",
        },
        {
          id: "demo-8",
          content:
            "Việc bón phân cho cây cảnh trong nhà rất quan trọng! Bạn đang trồng loại cây nào? Thông thường, cây cảnh trong nhà cần bón phân vào mùa xuân và hè (mùa sinh trưởng) với tần suất 2-4 tuần/lần.",
          sender: "bot",
          timestamp: new Date(Date.now() - 1600000),
          type: "text",
        },
        {
          id: "demo-9",
          content: "Tôi có cây pothos và cây snake plant.",
          sender: "user",
          timestamp: new Date(Date.now() - 1500000),
          type: "text",
        },
        {
          id: "demo-10",
          content:
            "Cả hai loại cây này đều rất dễ chăm sóc! Pothos thích phân bón cân bằng NPK, bón 1 lần/tháng vào mùa sinh trưởng. Snake plant ít cần phân hơn, có thể bón 2-3 tháng/lần. Nhớ pha loãng phân bón theo hướng dẫn để tránh bỏng rễ nhé!",
          sender: "bot",
          timestamp: new Date(Date.now() - 1400000),
          type: "text",
        },
      ],
    },
    {
      id: 3,
      title: "Xử lý rệp xanh trên cây",
      messages: [
        {
          id: "demo-11",
          content:
            "Xin chào! Tôi là trợ lý AI chuyên về cây trồng. Bạn có thể gửi hình ảnh cây của mình để tôi phân tích hoặc đặt câu hỏi về chăm sóc cây trồng.",
          sender: "bot",
          timestamp: new Date(Date.now() - 300000),
          type: "text",
        },
        {
          id: "demo-12",
          content: "Cây của tôi có côn trùng nhỏ màu xanh trên lá, đó là gì?",
          sender: "user",
          timestamp: new Date(Date.now() - 200000),
          type: "text",
        },
        {
          id: "demo-13",
          content:
            "Nghe có vẻ như cây của bạn bị rệp xanh (aphids)! Đây là loại côn trùng hút nhựa cây rất phổ biến. Bạn có thể xử lý bằng cách: 1) Xịt nước mạnh để cuốn trôi rệp, 2) Dùng dung dịch xà phòng pha loãng, 3) Hoặc sử dụng dầu neem. Bạn có thể chụp ảnh để tôi xác định chính xác hơn không?",
          sender: "bot",
          timestamp: new Date(Date.now() - 100000),
          type: "text",
        },
      ],
    },
  ]);

  const loadDemoSession = (sessionId: number) => {
    const session = demoSessions.find((s) => s.id === sessionId);
    if (session) {
      onLoadHistory(session.messages);
    }
  };

  return (
    <div className="bg-gray-50 border-r border-gray-200 flex flex-col w-80 flex-shrink-0">
      {/* Header */}
      <div className="p-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-4 w-4 text-gray-600" />
          <span className="font-medium text-gray-900">Lịch sử Demo ({demoSessions.length})</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">Dữ liệu mẫu để demo chức năng</p>
      </div>

      {/* Demo Sessions */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {demoSessions.map((session) => (
          <div
            key={session.id}
            className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-white cursor-pointer transition-colors bg-gray-50"
            onClick={() => loadDemoSession(session.id)}
          >
            <p className="text-sm font-medium text-gray-900 mb-1">{session.title}</p>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <MessageCircle className="h-3 w-3" />
                <span>{session.messages.length - 1} tin nhắn</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          💡 Đây là dữ liệu demo để trải nghiệm chức năng lịch sử chat
        </p>
      </div>
    </div>
  );
}
