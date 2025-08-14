"use client";

import AppLayout from "@/components/layout/AppLayout";
import { CameraCapture } from "@/components/ui/camera-capture";
import { useIsMobile } from "@/hooks/useIsMobile";
import { fileToBase64, sendChatMessage, type ChatRequest } from "@/lib/chat-api";
import { Bot, Camera, Image as ImageIcon, Send, User, X } from "lucide-react";
import { useRef, useState } from "react";

type Message = {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  imageUrl?: string;
};

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content:
        "Xin chào! Tôi là trợ lý AI chăm sóc cây trồng. Bạn có thể hỏi tôi về cách chăm sóc cây hoặc gửi ảnh cây để tôi phân tích.",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMobile = useIsMobile();

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!inputMessage.trim() && !selectedImage) || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage.trim() || (selectedImage ? "Đã gửi ảnh cây trồng" : ""),
      sender: "user",
      timestamp: new Date(),
      imageUrl: selectedImage || undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = inputMessage.trim();
    setInputMessage("");
    setSelectedImage(null);
    setIsLoading(true);

    try {
      // Prepare chat request
      const chatRequest: ChatRequest = {
        message: messageText || (selectedImage ? "Phân tích ảnh cây này giúp tôi" : ""),
        session_id: sessionId || undefined,
      };

      // Convert image to base64 if present
      if (selectedFile) {
        try {
          const base64 = await fileToBase64(selectedFile);
          chatRequest.image_base64 = base64;
        } catch (error) {
          console.error("Failed to convert image to base64:", error);
        }
      }

      // Call the real API
      const response = await sendChatMessage(chatRequest);

      // Handle response
      if ('error' in response) {
        // Error response
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: `❌ Lỗi: ${response.message}`,
          sender: "bot",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        // Success response
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.message,
          sender: "bot",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMessage]);

        // Update session ID if provided
        if (response.session_id) {
          setSessionId(response.session_id);
        }
      }
    } catch (error) {
      console.error("Chat API error:", error);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "❌ Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } finally {
      setIsLoading(false);
      setSelectedFile(null);
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setSelectedFile(null);
  };

  const handleCameraCapture = (imageDataUrl: string) => {
    setSelectedImage(imageDataUrl);
    setShowCamera(false);

    // Convert data URL to File object
    const base64Data = imageDataUrl.split(',')[1];
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const file = new File([byteArray], `camera-capture-${Date.now()}.jpg`, { type: 'image/jpeg' });
    setSelectedFile(file);
  };

  const handleImageButtonClick = () => {
    if (isMobile && typeof navigator !== "undefined" && navigator.mediaDevices) {
      setShowCamera(true);
    } else {
      fileInputRef.current?.click();
    }
  };

  return (
    <AppLayout title="Plant Assistant AI" subtitle="Trợ lý AI chăm sóc cây trồng">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg h-[calc(100dvh-5rem)] flex flex-col">
          <div className="p-4 md:p-6 border-b border-gray-200">
            <h1 className="text-xl md:text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Bot className="h-6 w-6 md:h-8 md:w-8 text-green-600" />
              Plant Care Assistant
            </h1>
            <p className="text-gray-600 mt-1 text-sm md:text-base">
              Hỏi tôi bất cứ điều gì về chăm sóc cây, tưới nước, ánh sáng và nhiều hơn nữa!
            </p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.sender === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.sender === "user"
                      ? "bg-blue-100 text-blue-600"
                      : "bg-green-100 text-green-600"
                  }`}
                >
                  {message.sender === "user" ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>

                <div
                  className={`max-w-[85%] md:max-w-[70%] rounded-lg p-3 ${
                    message.sender === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  {message.imageUrl && (
                    <div className="mb-2">
                      <img
                        src={message.imageUrl}
                        alt="Uploaded plant"
                        className="max-w-full h-auto rounded-lg max-h-48 object-cover"
                      />
                    </div>
                  )}
                  <p className="text-sm">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.sender === "user" ? "text-blue-100" : "text-gray-500"
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSendMessage} className="p-4 md:p-6 border-t border-gray-200">
            {/* Image Preview */}
            {selectedImage && (
              <div className="mb-4 relative inline-block">
                <img
                  src={selectedImage}
                  alt="Selected"
                  className="max-w-32 h-24 object-cover rounded-lg border"
                />
                <button
                  type="button"
                  onClick={removeImage}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            )}

            <div className="flex gap-2">
              <div className="flex-1 flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Hỏi về chăm sóc cây hoặc gửi ảnh..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm md:text-base w-[5px]"
                  disabled={isLoading}
                />

                {/* Image Upload/Camera Button */}
                {isMobile && typeof navigator !== "undefined" && navigator.mediaDevices && (
                  <button
                    type="button"
                    onClick={handleImageButtonClick}
                    className="p-2 text-gray-500 hover:text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                    title="Chụp ảnh"
                  >
                    <Camera className="h-5 w-5" />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-500 hover:text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  title="Tải ảnh lên"
                >
                  <ImageIcon className="h-5 w-5" />
                </button>
              </div>

              <button
                type="submit"
                disabled={(!inputMessage.trim() && !selectedImage) || isLoading}
                className="px-4 md:px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
                <span className="hidden md:inline">Gửi</span>
              </button>
            </div>

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
          </form>
        </div>

        {/* Camera Component */}
        {showCamera && (
          <CameraCapture
            onImageCapture={handleCameraCapture}
            onClose={() => setShowCamera(false)}
          />
        )}
      </div>
    </AppLayout>
  );
}
