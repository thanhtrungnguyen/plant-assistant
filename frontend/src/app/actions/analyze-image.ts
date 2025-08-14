"use server";

export interface AnalysisResult {
  plantType: string;
  health: string;
  confidence: number;
  disease: string;
  description: string;
  treatment: string;
  prevention: string;
  recommendations: string[];
}

export async function analyzeImage(imageDataUrl: string): Promise<AnalysisResult> {
  // Simulate API call delay
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // Mock analysis result based on image analysis
  const mockResults: AnalysisResult[] = [
    {
      plantType: "Pothos (Epipremnum aureum)",
      health: "Khỏe mạnh",
      confidence: 0.92,
      disease: "Không phát hiện bệnh",
      description: "Cây Pothos của bạn có vẻ rất khỏe mạnh với lá xanh tươi và bóng.",
      treatment: "Không cần điều trị đặc biệt, tiếp tục chăm sóc như hiện tại.",
      prevention: "Tránh tưới nước quá nhiều và đặt ở nơi có ánh sáng gián tiếp.",
      recommendations: [
        "Cây trồng đang trong tình trạng tốt",
        "Tiếp tục tưới nước 1-2 lần/tuần",
        "Đặt ở nơi có ánh sáng gián tiếp",
        "Bón phân NPK pha loãng mỗi tháng",
      ],
    },
    {
      plantType: "Monstera Deliciosa",
      health: "Có dấu hiệu bệnh",
      confidence: 0.85,
      disease: "Đốm lá nâu",
      description:
        "Phát hiện một số đốm nâu trên lá, có thể do tưới nước quá nhiều hoặc độ ẩm cao.",
      treatment: "Cắt bỏ lá bị bệnh, giảm tần suất tưới nước và tăng thông gió.",
      prevention: "Tránh nước đọng lại trên lá, tưới nước vào buổi sáng để lá khô nhanh.",
      recommendations: [
        "Cắt bỏ lá bị đốm nâu",
        "Giảm tưới nước xuống 1 lần/tuần",
        "Tăng thông gió xung quanh cây",
        "Kiểm tra dẫn nước của chậu",
      ],
    },
    {
      plantType: "Snake Plant (Sansevieria)",
      health: "Cần chăm sóc",
      confidence: 0.78,
      disease: "Thối rễ",
      description: "Lá vàng và mềm có thể là dấu hiệu của thối rễ do tưới nước quá nhiều.",
      treatment: "Lấy cây ra khỏi chậu, cắt bỏ rễ thối, thay đất mới và giảm tưới nước.",
      prevention: "Chỉ tưới nước khi đất khô hoàn toàn, đảm bảo chậu có lỗ thoát nước.",
      recommendations: [
        "Kiểm tra và cắt bỏ rễ thối",
        "Thay đất mới có thoát nước tốt",
        "Giảm tưới nước xuống 1 lần/2 tuần",
        "Đặt ở nơi có ánh sáng đủ",
      ],
    },
  ];

  // Randomly select a result for demo purposes
  const randomIndex = Math.floor(Math.random() * mockResults.length);
  return mockResults[randomIndex];
}
