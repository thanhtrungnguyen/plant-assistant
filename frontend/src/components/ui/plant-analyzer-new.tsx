"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Image as ImageIcon, Search, Upload } from "lucide-react";
import { useRef, useState } from "react";

interface AnalysisResult {
  plantType: string;
  health: string;
  confidence: number;
  recommendations: string[];
}

export function PlantAnalyzer() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
        setAnalysisResult(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);

    // Simulate AI analysis
    setTimeout(() => {
      const mockResult: AnalysisResult = {
        plantType: "Pothos (Epipremnum aureum)",
        health: "Khỏe mạnh",
        confidence: 0.92,
        recommendations: [
          "Cây trồng đang trong tình trạng tốt",
          "Tiếp tục tưới nước 1-2 lần/tuần",
          "Đặt ở nơi có ánh sáng gián tiếp",
          "Bón phân NPK pha loãng mỗi tháng"
        ]
      };
      setAnalysisResult(mockResult);
      setIsAnalyzing(false);
    }, 3000);
  };

  const handleReset = () => {
    setSelectedImage(null);
    setAnalysisResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl md:text-2xl text-center">
            Tải lên hình ảnh cây trồng
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!selectedImage ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-500 transition-colors">
              <div className="space-y-4">
                <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                  <Upload className="w-8 h-8 text-gray-400" />
                </div>
                <div>
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    Chọn hình ảnh để phân tích
                  </p>
                  <p className="text-sm text-gray-500 mb-4">
                    Hỗ trợ định dạng JPG, PNG, GIF (tối đa 10MB)
                  </p>
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <Button
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <ImageIcon className="w-4 h-4 mr-2" />
                      Chọn từ thiết bị
                    </Button>
                    <Button
                      variant="outline"
                      className="border-green-500 text-green-600 hover:bg-green-50"
                    >
                      <Search className="w-4 h-4 mr-2" />
                      Chụp ảnh
                    </Button>
                  </div>
                </div>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative">
                <img
                  src={selectedImage}
                  alt="Uploaded plant"
                  className="w-full h-64 md:h-80 object-cover rounded-lg"
                />
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  {isAnalyzing ? "Đang phân tích..." : "Phân tích bằng AI"}
                </Button>
                <Button
                  onClick={handleReset}
                  variant="outline"
                  className="flex-1"
                >
                  Chọn ảnh khác
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Loading */}
      {isAnalyzing && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  AI đang phân tích hình ảnh...
                </h3>
                <p className="text-gray-600">
                  Vui lòng đợi trong giây lát để nhận kết quả chi tiết
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-green-700">
              Kết quả phân tích
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Loại cây</h4>
                <p className="text-sm md:text-base text-gray-700 mb-1">{analysisResult.plantType}</p>
                <p className="text-xs md:text-sm text-gray-500">
                  Độ tin cậy: {Math.round(analysisResult.confidence * 100)}%
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Tình trạng sức khỏe</h4>
                <p className="text-sm md:text-base text-gray-700">{analysisResult.health}</p>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Khuyến nghị chăm sóc</h4>
              <ul className="space-y-2">
                {analysisResult.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-green-600 mt-1">•</span>
                    <span className="text-sm md:text-base text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <Button
                onClick={handleReset}
                variant="outline"
                className="w-full"
              >
                Phân tích ảnh khác
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
