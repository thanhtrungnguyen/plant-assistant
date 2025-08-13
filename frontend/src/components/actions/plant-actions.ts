"use server";

import { cookies } from "next/headers";

// Types for plant analysis
export interface PlantAnalysisRequest {
  image: string; // base64 encoded image
  prompt?: string;
}

export interface PlantAnalysisResult {
  plantName: string;
  health: "healthy" | "needs_attention" | "sick";
  confidence: number;
  issues?: string[];
  recommendations?: string[];
  watering?: {
    frequency: string;
    amount: string;
  };
  lighting?: string;
  temperature?: string;
  humidity?: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  type: "text" | "image" | "analysis";
  imageUrl?: string;
  analysis?: PlantAnalysisResult;
}

export interface PlantCareStats {
  totalPlants: number;
  healthyPlants: number;
  needsAttention: number;
  needsWatering: number;
  plantTypes: number;
}

// Mock API functions (replace with actual API calls)
export async function analyzePlantImage(imageData: string): Promise<PlantAnalysisResult> {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    throw new Error("No access token found");
  }

  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Mock analysis result
  const mockResults: PlantAnalysisResult[] = [
    {
      plantName: "Cây Pothos (Epipremnum aureum)",
      health: "healthy",
      confidence: 92,
      recommendations: [
        "Cây đang phát triển tốt",
        "Duy trì độ ẩm đất ổn định",
        "Đặt ở nơi có ánh sáng gián tiếp",
        "Bón phân 2 tuần một lần"
      ],
      watering: {
        frequency: "2-3 lần/tuần",
        amount: "200-300ml"
      },
      lighting: "Ánh sáng gián tiếp",
      temperature: "18-24°C",
      humidity: "40-60%"
    },
    {
      plantName: "Cây Monstera Deliciosa",
      health: "needs_attention",
      confidence: 85,
      issues: ["Lá có dấu hiệu úng nước", "Thiếu ánh sáng"],
      recommendations: [
        "Giảm tần suất tưới nước",
        "Di chuyển cây ra gần cửa sổ",
        "Kiểm tra hệ thống thoát nước",
        "Cắt bỏ lá bị hỏng"
      ],
      watering: {
        frequency: "1-2 lần/tuần",
        amount: "150-250ml"
      },
      lighting: "Ánh sáng gián tiếp mạnh",
      temperature: "20-26°C",
      humidity: "50-70%"
    },
    {
      plantName: "Cây Cactus",
      health: "healthy",
      confidence: 95,
      recommendations: [
        "Cây rất khỏe mạnh",
        "Tiếp tục chế độ chăm sóc hiện tại",
        "Đảm bảo đất khô ráo giữa các lần tưới"
      ],
      watering: {
        frequency: "1 lần/tuần (mùa hè), 2 tuần/lần (mùa đông)",
        amount: "50-100ml"
      },
      lighting: "Ánh sáng trực tiếp",
      temperature: "18-30°C",
      humidity: "30-50%"
    }
  ];

  // Return random result for demo
  return mockResults[Math.floor(Math.random() * mockResults.length)];
}

export async function sendChatMessage(message: string): Promise<string> {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    throw new Error("No access token found");
  }

  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Generate bot response based on message content
  const lowerMessage = message.toLowerCase();

  if (lowerMessage.includes("tưới") || lowerMessage.includes("nước")) {
    return "Việc tưới nước phụ thuộc vào loại cây và điều kiện môi trường. Thông thường, bạn nên kiểm tra độ ẩm của đất bằng cách nhấn ngón tay xuống đất 2-3cm. Nếu đất khô thì cần tưới nước. Đối với hầu hết cây cảnh trong nhà, tưới 2-3 lần/tuần là phù hợp.";
  }

  if (lowerMessage.includes("ánh sáng") || lowerMessage.includes("nắng")) {
    return "Hầu hết các cây cảnh cần ánh sáng gián tiếp từ 6-8 tiếng mỗi ngày. Tránh để cây dưới ánh nắng trực tiếp quá lâu vì có thể làm cháy lá. Nếu nhà bạn thiếu ánh sáng tự nhiên, có thể sử dụng đèn LED grow light.";
  }

  if (lowerMessage.includes("phân bón") || lowerMessage.includes("bón phân")) {
    return "Bón phân cho cây 2-4 tuần một lần trong mùa sinh trưởng (mùa xuân và hè). Sử dụng phân hữu cơ hoặc phân NPK pha loãng theo hướng dẫn trên bao bì. Trong mùa đông, giảm tần suất bón phân xuống 1-2 tháng/lần.";
  }

  if (lowerMessage.includes("bệnh") || lowerMessage.includes("sâu") || lowerMessage.includes("côn trùng")) {
    return "Để phòng ngừa sâu bệnh, hãy đảm bảo cây có thông gió tốt, tránh tưới nước lên lá, và kiểm tra cây thường xuyên. Nếu phát hiện sâu bệnh, có thể sử dụng dung dịch xà phòng pha loãng hoặc neem oil. Gửi hình ảnh để tôi hỗ trợ chẩn đoán cụ thể.";
  }

  if (lowerMessage.includes("vàng lá") || lowerMessage.includes("lá vàng")) {
    return "Lá vàng có thể do nhiều nguyên nhân: tưới quá nhiều nước, thiếu ánh sáng, thiếu dinh dưỡng, hoặc quá trình lão hóa tự nhiên. Hãy kiểm tra độ ẩm đất, vị trí đặt cây, và lịch bón phân. Cắt bỏ lá vàng để cây tập trung dinh dưỡng cho lá khỏe mạnh.";
  }

  if (lowerMessage.includes("chậu") || lowerMessage.includes("thay chậu")) {
    return "Thay chậu khi rễ cây đã lấp đầy chậu cũ (thường 1-2 năm/lần). Chọn chậu lớn hơn 2-3cm so với chậu cũ, có lỗ thoát nước tốt. Thời điểm tốt nhất là đầu mùa xuân khi cây bắt đầu sinh trưởng mạnh.";
  }

  if (lowerMessage.includes("nhiệt độ") || lowerMessage.includes("khí hậu")) {
    return "Hầu hết cây cảnh trong nhà phát triển tốt ở nhiệt độ 18-24°C. Tránh đặt cây gần điều hòa, máy sưởi, hoặc cửa sổ có gió lùa. Độ ẩm lý tưởng là 40-60%, có thể tăng độ ẩm bằng cách đặt khay nước gần cây.";
  }

  // Default response
  return "Cảm ơn bạn đã hỏi! Để tôi có thể hỗ trợ tốt hơn, bạn có thể gửi hình ảnh cây của mình hoặc mô tả chi tiết hơn về vấn đề bạn gặp phải. Tôi có thể tư vấn về tưới nước, ánh sáng, bón phân, chữa bệnh và nhiều vấn đề khác về chăm sóc cây trồng.";
}

// Plant management functions
export interface Plant {
  id: string;
  name: string;
  type: string;
  health: "healthy" | "needs_attention" | "sick";
  lastWatered: Date;
  nextWateringDue: Date;
  location: string;
  notes?: string;
  imageUrl?: string;
}

export async function fetchUserPlants(): Promise<Plant[]> {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    // Return mock data when no token
    console.log("No access token found, using mock data");
  }

  // Mock data
  await new Promise(resolve => setTimeout(resolve, 500));

  const mockPlants: Plant[] = [
    {
      id: "1",
      name: "Pothos của tôi",
      type: "Epipremnum aureum",
      health: "healthy",
      lastWatered: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
      nextWateringDue: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
      location: "Phòng khách",
      notes: "Đang phát triển rất tốt"
    },
    {
      id: "2",
      name: "Monstera xinh đẹp",
      type: "Monstera Deliciosa",
      health: "needs_attention",
      lastWatered: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
      nextWateringDue: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      location: "Phòng ngủ",
      notes: "Cần chú ý độ ẩm"
    },
    {
      id: "3",
      name: "Xương rồng mini",
      type: "Cactaceae",
      health: "healthy",
      lastWatered: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
      nextWateringDue: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000),
      location: "Ban công",
      notes: "Rất dễ chăm sóc"
    }
  ];

  return mockPlants;
}

export async function getPlantCareStats() {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    // Return mock data when no token
    console.log("No access token found, using mock stats");
    return {
      totalPlants: 15,
      healthyPlants: 12,
      needsAttention: 2,
      needsWatering: 3,
      plantTypes: 5
    };
  }

  const plants = await fetchUserPlants();

  return {
    totalPlants: plants.length,
    healthyPlants: plants.filter(p => p.health === "healthy").length,
    needsAttention: plants.filter(p => p.health === "needs_attention").length,
    needsWatering: plants.filter(p => p.nextWateringDue <= new Date()).length,
    plantTypes: [...new Set(plants.map(p => p.type))].length
  };
}
