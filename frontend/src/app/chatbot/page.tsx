"use client";

import AppLayout from "@/components/layout/AppLayout";
import { CameraCapture } from "@/components/ui/camera-capture";
import { ChatHistoryPanel } from "@/components/ui/chat-history-panel";
import { DemoHistoryButton } from "@/components/ui/demo-history-sidebar";
import { Message, useChat, useChatSessions } from "@/hooks/useChat";
import { useIsMobile } from "@/hooks/useIsMobile";
import { AlertCircle, Bot, Camera, History, Image as ImageIcon, Send, User, X } from "lucide-react";
import { useRef, useState } from "react";

export default function ChatbotPage() {
  const {
    messages,
    isLoading,
    currentSession,
    error: chatError,
    sendMessage,
    clearMessages,
    createNewSession,
    loadSession,
  } = useChat({
    useRag: true,
    onError: (error) => {
      console.error("Chat error:", error);
    },
  });

  const { sessions, loadSessions } = useChatSessions();

  const [inputMessage, setInputMessage] = useState("");
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [showMobileHistory, setShowMobileHistory] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMobile = useIsMobile();

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!inputMessage.trim() && !selectedImage) || isLoading) return;

    try {
      await sendMessage(inputMessage, selectedImage || undefined);
      setInputMessage("");
      setSelectedImage(null);
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
  };

  const handleCameraCapture = (imageDataUrl: string) => {
    setSelectedImage(imageDataUrl);
    setShowCamera(false);
  };

  const handleLoadHistory = async (historyMessages: Message[]) => {
    // For now, we'll just clear and set messages
    // In a real implementation, you might want to load a specific session
    clearMessages();
    // You could implement session loading here
  };

  const handleNewChat = async () => {
    try {
      await createNewSession();
    } catch (error) {
      console.error("Failed to create new session:", error);
    }
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
      <div className="flex h-[calc(100vh-8rem)] lg:h-[calc(100vh-12rem)]">
        {/* Chat History Sidebar - Hidden on mobile */}
        <div className="hidden lg:block">
          <DemoHistoryButton onLoadHistory={handleLoadHistory} />
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-white rounded-lg shadow-lg">
          {/* Error Display */}
          {chatError && (
            <div className="p-3 md:p-4 bg-red-50 border-b border-red-200">
              <div className="flex items-center space-x-2 text-red-600">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{chatError}</span>
              </div>
            </div>
          )}

          {/* Header - Responsive */}
          <div className="p-3 md:p-6 border-b border-gray-200 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-lg md:text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Bot className="h-5 w-5 md:h-8 md:w-8 text-green-600" />
                  <span className="hidden sm:inline">Plant Care Assistant</span>
                  <span className="sm:hidden">Plant AI</span>
                </h1>
                <p className="text-gray-600 mt-1 text-xs md:text-base">
                  <span className="hidden sm:inline">Hỏi tôi bất cứ điều gì về chăm sóc cây, tưới nước, ánh sáng và nhiều hơn nữa!</span>
                  <span className="sm:hidden">Trợ lý AI chăm sóc cây trồng</span>
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleNewChat}
                  className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Cuộc trò chuyện mới
                </button>
                {/* History button for mobile */}
                <button
                  onClick={() => setShowMobileHistory(true)}
                  className="lg:hidden p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Xem lịch sử trò chuyện"
                >
                  <History className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Messages Area - Scrollable */}
          <div className="flex-1 overflow-y-auto p-3 md:p-6 space-y-3 md:space-y-4 min-h-0">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-2 md:gap-3 ${
                  message.sender === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex-shrink-0 w-7 h-7 md:w-8 md:h-8 rounded-full flex items-center justify-center ${
                    message.sender === "user"
                      ? "bg-blue-100 text-blue-600"
                      : "bg-green-100 text-green-600"
                  }`}
                >
                  {message.sender === "user" ? (
                    <User className="h-3 w-3 md:h-4 md:w-4" />
                  ) : (
                    <Bot className="h-3 w-3 md:h-4 md:w-4" />
                  )}
                </div>

                <div
                  className={`max-w-[80%] md:max-w-[70%] rounded-lg p-2 md:p-3 ${
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
                        className="max-w-full h-auto rounded-lg max-h-32 md:max-h-48 object-cover"
                      />
                    </div>
                  )}
                  <p className="text-xs md:text-sm">{message.content}</p>
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
              <div className="flex items-start gap-2 md:gap-3">
                <div className="flex-shrink-0 w-7 h-7 md:w-8 md:h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                  <Bot className="h-3 w-3 md:h-4 md:w-4" />
                </div>
                <div className="bg-gray-100 rounded-lg p-2 md:p-3">
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

          {/* Input Form - Fixed at bottom */}
          <form onSubmit={handleSendMessage} className="p-3 md:p-6 border-t border-gray-200 flex-shrink-0">
            {/* Image Preview */}
            {selectedImage && (
              <div className="mb-3 relative inline-block">
                <img
                  src={selectedImage}
                  alt="Selected"
                  className="w-20 h-16 md:w-32 md:h-24 object-cover rounded-lg border"
                />
                <button
                  type="button"
                  onClick={removeImage}
                  className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 md:w-6 md:h-6 flex items-center justify-center text-xs hover:bg-red-600"
                >
                  <X className="h-2 w-2 md:h-3 md:w-3" />
                </button>
              </div>
            )}

            <div className="flex gap-2">
              <div className="flex-1 flex gap-1 md:gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Hỏi về chăm sóc cây..."
                  className="flex-1 px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm md:text-base min-w-0"
                  disabled={isLoading}
                />

                {/* Camera/Image Upload Buttons */}
                {isMobile && typeof navigator !== "undefined" && navigator.mediaDevices && (
                  <button
                    type="button"
                    onClick={handleImageButtonClick}
                    className="p-2 text-gray-500 hover:text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 flex-shrink-0"
                    title="Chụp ảnh"
                  >
                    <Camera className="h-4 w-4 md:h-5 md:w-5" />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-500 hover:text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 flex-shrink-0"
                  title="Tải ảnh lên"
                >
                  <ImageIcon className="h-4 w-4 md:h-5 md:w-5" />
                </button>
              </div>

              <button
                type="submit"
                disabled={(!inputMessage.trim() && !selectedImage) || isLoading}
                className="px-3 md:px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 flex-shrink-0"
              >
                <Send className="h-3 w-3 md:h-4 md:w-4" />
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

        {/* Mobile History Panel */}
        {showMobileHistory && (
          <ChatHistoryPanel
            isOpen={showMobileHistory}
            onClose={() => setShowMobileHistory(false)}
            onLoadHistory={(messages) => {
              handleLoadHistory(messages);
              setShowMobileHistory(false);
            }}
          />
        )}
      </div>
    </AppLayout>
  );
}
