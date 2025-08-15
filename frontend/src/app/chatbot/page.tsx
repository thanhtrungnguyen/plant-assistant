"use client";

import AppLayout from "@/components/layout/AppLayout";
import { CameraCapture } from "@/components/ui/camera-capture";
import { useIsMobile } from "@/hooks/useIsMobile";
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
  const [isLoading, setIsLoading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
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
    setInputMessage("");
    setSelectedImage(null);
    setIsLoading(true);

    // Simulate bot response
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: selectedImage ? getImageAnalysisResponse() : getBotResponse(userMessage.content),
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsLoading(false);
    }, 1500);
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

  const handleImageButtonClick = () => {
    if (isMobile && typeof navigator !== "undefined" && navigator.mediaDevices) {
      setShowCamera(true);
    } else {
      fileInputRef.current?.click();
    }
  };

  const getImageAnalysisResponse = (): string => {
    const responses = [
      "Tôi thấy đây là một cây Pothos khỏe mạnh! Lá xanh tươi cho thấy cây đang được chăm sóc tốt. Để duy trì, hãy tưới nước khi đất khô và đặt ở nơi có ánh sáng gián tiếp.",
      "Cây Monstera của bạn có vẻ cần nhiều ánh sáng hơn. Tôi khuyên nên di chuyển cây gần cửa sổ hơn và kiểm tra độ ẩm đất thường xuyên.",
      "Đây có vẻ là cây Snake Plant. Cây này rất dễ chăm sóc! Chỉ cần tưới nước 1-2 lần/tháng và cây sẽ phát triển tốt ngay cả trong điều kiện ánh sáng thấp.",
      "Tôi nhận thấy một số dấu hiệu vàng lá. Điều này có thể do tưới nước quá nhiều. Hãy kiểm tra xem đất có bị úng nước không và giảm tần suất tưới nước.",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const getBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();

    if (input.includes("tưới") || input.includes("nước")) {
      return "Để tưới nước đúng cách, hãy kiểm tra độ ẩm đất bằng cách nhấn ngón tay xuống đất 2-3cm. Hầu hết các cây cần tưới khi lớp đất trên cùng khô. Thông thường tưới 1-2 lần/tuần, tùy thuộc vào loại cây và mùa.";
    }

    if (input.includes("ánh sáng") || input.includes("nắng")) {
      return "Yêu cầu ánh sáng khác nhau tùy loại cây. Hầu hết cây trong nhà thích ánh sáng gián tiếp sáng. Tránh ánh nắng trực tiếp có thể làm cháy lá. Nếu lá vàng hoặc cây héo, có thể cây cần nhiều ánh sáng hơn.";
    }

    if (input.includes("bón phân") || input.includes("dinh dưỡng")) {
      return "Bón phân cho cây trong mùa sinh trưởng (xuân/hè) bằng phân bón lỏng cân bằng 2-4 tuần/lần. Giảm hoặc ngừng bón phân vào thu/đông khi cây phát triển chậm lại.";
    }

    if (input.includes("sâu bệnh") || input.includes("côn trùng")) {
      return "Dấu hiệu sâu bệnh thường là lá vàng, chất dính hoặc thấy côn trùng. Kiểm tra thường xuyên và xử lý bằng xà phòng diệt côn trùng hoặc dầu neem. Cách ly cây bị nhiễm bệnh.";
    }

    if (input.includes("thay chậu") || input.includes("chậu mới")) {
      return "Thay chậu khi rễ mọc ra khỏi lỗ thoát nước hoặc đất cạn kiệt nhanh. Chọn chậu lớn hơn 2-3cm, dùng đất trồng mới, tốt nhất là thay chậu vào mùa xuân.";
    }

    if (input.includes("ảnh") || input.includes("hình")) {
      return "Bạn có thể gửi ảnh cây trồng cho tôi để phân tích! Tôi sẽ giúp nhận dạng loại cây và đưa ra lời khuyên chăm sóc cụ thể.";
    }

    return "Tôi có thể giúp bạn về tưới nước, ánh sáng, bón phân, phòng trừ sâu bệnh, thay chậu và phân tích ảnh cây trồng. Bạn muốn hỏi gì cụ thể hơn không?";
  };

  return (
    <AppLayout title="Plant Assistant AI" subtitle="Trợ lý AI chăm sóc cây trồng">
      <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] lg:h-[calc(100vh-12rem)]">
        <div className="bg-white rounded-lg shadow-lg h-full flex flex-col">
          {/* Header - Responsive */}
          <div className="p-3 md:p-6 border-b border-gray-200 flex-shrink-0">
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
      </div>
    </AppLayout>
  );
}
