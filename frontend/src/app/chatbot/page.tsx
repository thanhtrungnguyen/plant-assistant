"use client";

import AppLayout from "@/components/layout/AppLayout";
import { CameraCapture } from "@/components/ui/camera-capture";
import { ConversationHistorySidebar } from "@/components/ui/conversation-history-sidebar";
import { MobileChatHistoryPanel } from "@/components/ui/mobile-chat-history-panel";
import { useChat } from "@/hooks/useChat";
import { useIsMobile } from "@/hooks/useIsMobile";
import { ChatApiError } from "@/lib/chat-api";
import { Bot, Camera, History, Image as ImageIcon, Send, User, X } from "lucide-react";
import { useRef, useState } from "react";

// Client-side timestamp component to prevent hydration mismatch
function ClientTimestamp({ timestamp, className }: { timestamp: Date; className?: string }) {
  return <span className={className}>{timestamp.toLocaleTimeString()}</span>;
}

export default function ChatbotPage() {
  const [inputMessage, setInputMessage] = useState("");
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [showMobileHistory, setShowMobileHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMobile = useIsMobile();

  const {
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
  } = useChat({
    onError: (error: ChatApiError) => {
      if (error.status === 401) {
        setError("Bạn cần đăng nhập để sử dụng tính năng chat.");
      } else {
        setError(error.message);
      }
    },
  });

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!inputMessage.trim() && !selectedImage) || isLoading) return;

    setError(null); // Clear any previous errors

    await sendMessage(inputMessage, selectedImage || undefined);

    setInputMessage("");
    setSelectedImage(null);
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

  const handleMobileHistoryClick = () => {
    loadConversations(); // Load conversations when opening mobile history
    setShowMobileHistory(true);
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
        {/* Conversation History Sidebar - Hidden on mobile */}
        <div className="hidden lg:block">
          <ConversationHistorySidebar
            conversations={conversations}
            currentConversationId={currentConversationId}
            isLoading={isLoadingConversations}
            onLoadConversations={loadConversations}
            onSelectConversation={loadConversation}
            onNewConversation={startNewConversation}
            onDeleteConversation={deleteConversation}
          />
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-white rounded-lg shadow-lg">
          {/* Header - Responsive */}
          <div className="p-3 md:p-6 border-b border-gray-200 flex-shrink-0 relative">
            <h1 className="text-lg md:text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Bot className="h-5 w-5 md:h-8 md:w-8 text-green-600" />
              <span className="hidden sm:inline">Plant Care Assistant</span>
              <span className="sm:hidden">Plant AI</span>
            </h1>
            <p className="text-gray-600 mt-1 text-xs md:text-base">
              <span className="hidden sm:inline">
                Hỏi tôi bất cứ điều gì về chăm sóc cây, tưới nước, ánh sáng và nhiều hơn nữa!
              </span>
              <span className="sm:hidden">Trợ lý AI chăm sóc cây trồng</span>
            </p>

            {/* Mobile History Button */}
            {isMobile && (
              <button
                onClick={handleMobileHistoryClick}
                className="absolute top-3 right-3 p-2 text-gray-500 hover:text-gray-700 lg:hidden"
              >
                <History className="h-5 w-5" />
              </button>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mx-3 md:mx-6 mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

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

                  {message.isLoading ? (
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
                  ) : (
                    <>
                      <p className="text-xs md:text-sm">{message.content}</p>
                      <ClientTimestamp
                        timestamp={message.timestamp}
                        className={`text-xs mt-1 ${
                          message.sender === "user" ? "text-blue-100" : "text-gray-500"
                        }`}
                      />
                    </>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form - Fixed at bottom */}
          <form
            onSubmit={handleSendMessage}
            className="p-3 md:p-6 border-t border-gray-200 flex-shrink-0"
          >
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
          <MobileChatHistoryPanel
            isOpen={showMobileHistory}
            conversations={conversations}
            currentConversationId={currentConversationId}
            isLoading={isLoadingConversations}
            onClose={() => setShowMobileHistory(false)}
            onSelectConversation={loadConversation}
            onNewConversation={startNewConversation}
            onDeleteConversation={deleteConversation}
          />
        )}
      </div>
    </AppLayout>
  );
}
