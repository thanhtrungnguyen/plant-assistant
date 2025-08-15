"use client";

import { AnalysisError, AnalysisResult, analyzeImage } from "@/app/actions/analyze-image";
import { Button } from "@/components/ui/button";
import { CameraCapture } from "@/components/ui/camera-capture";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useIsMobile } from "@/hooks/useIsMobile";
import { Camera, Image as ImageIcon, Upload } from "lucide-react";
import { useRef, useState } from "react";

export function PlantAnalyzer() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<AnalysisError | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMobile = useIsMobile();

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
        setAnalysisResult(null);
        setError(null);
      };
      reader.onerror = (e) => {
        console.error("File read error:", e);
        setError({
          message: "Không thể đọc file ảnh. Vui lòng thử lại.",
          type: "error",
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const result = await analyzeImage(selectedImage);

      // Check if result is an error response
      if ("message" in result && "type" in result) {
        const errorResult = result as AnalysisError;
        setError(errorResult);
      } else {
        // Result is AnalysisResult
        setAnalysisResult(result as AnalysisResult);
      }
    } catch (error) {
      console.error("Analysis failed:", error);
      let errorMessage = "Đã xảy ra lỗi khi phân tích hình ảnh. Vui lòng thử lại.";

      if (error instanceof Error) {
        errorMessage = error.message;
      }

      setError({
        message: errorMessage,
        type: "error",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };
  const handleReset = () => {
    setSelectedImage(null);
    setAnalysisResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleCameraCapture = (imageDataUrl: string) => {
    setSelectedImage(imageDataUrl);
    setAnalysisResult(null);
    setError(null);
    setShowCamera(false);
  };

  const handleImageButtonClick = () => {
    if (isMobile && typeof navigator !== "undefined" && navigator.mediaDevices) {
      setShowCamera(true);
    } else {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg md:text-2xl text-center">
            Tải lên hình ảnh cây trồng
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!selectedImage ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 md:p-8 text-center hover:border-green-500 transition-colors">
              <div className="space-y-3 md:space-y-4">
                <div className="mx-auto w-12 h-12 md:w-16 md:h-16 bg-gray-100 rounded-full flex items-center justify-center">
                  <Upload className="w-6 h-6 md:w-8 md:h-8 text-gray-400" />
                </div>
                <div>
                  <p className="text-base md:text-lg font-medium text-gray-700 mb-2">
                    Chọn hình ảnh để phân tích
                  </p>
                  <p className="text-xs md:text-sm text-gray-500 mb-4">
                    Hỗ trợ định dạng JPG, PNG, GIF (tối đa 10MB)
                  </p>
                  <div className="flex flex-col sm:flex-row gap-2 md:gap-3 justify-center">
                    {isMobile && typeof navigator !== "undefined" && navigator.mediaDevices ? (
                      <Button
                        onClick={() => setShowCamera(true)}
                        className="bg-green-600 hover:bg-green-700 text-sm md:text-base"
                      >
                        <Camera className="w-3 h-3 md:w-4 md:h-4 mr-2" />
                        Chụp ảnh
                      </Button>
                    ) : null}
                    <Button
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-green-600 hover:bg-green-700 text-sm md:text-base"
                    >
                      <ImageIcon className="w-3 h-3 md:w-4 md:h-4 mr-2" />
                      Chọn từ thiết bị
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
            <div className="space-y-3 md:space-y-4">
              <div className="relative">
                <img
                  src={selectedImage}
                  alt="Uploaded plant"
                  className="w-full h-48 md:h-80 object-cover rounded-lg"
                />
              </div>
              <div className="flex flex-col sm:flex-row gap-2 md:gap-3">
                <Button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-sm md:text-base"
                >
                  {isAnalyzing ? "Đang phân tích..." : "Phân tích bằng AI"}
                </Button>
                <Button
                  onClick={handleReset}
                  variant="outline"
                  className="flex-1 text-sm md:text-base"
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
          <CardContent className="p-4 md:p-8 text-center">
            <div className="space-y-3 md:space-y-4">
              <div className="mx-auto w-12 h-12 md:w-16 md:h-16 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div>
              <div>
                <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-2">
                  AI đang phân tích hình ảnh...
                </h3>
                <p className="text-sm md:text-base text-gray-600">
                  Vui lòng đợi trong giây lát để nhận kết quả chi tiết
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-3 md:p-6">
            <div className="flex items-center gap-2 text-red-700">
              <div className="w-4 h-4 md:w-5 md:h-5 rounded-full flex items-center justify-center flex-shrink-0 bg-red-200">
                <span className="text-xs font-bold text-red-700">!</span>
              </div>
              <div>
                <h4 className="font-semibold mb-1 text-sm md:text-base">Lỗi phân tích</h4>
                <p className="text-xs md:text-sm">{error.message}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-2 text-xs underline hover:no-underline"
                >
                  Đóng
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}{" "}
      {/* Results */}
      {analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg md:text-xl text-green-700">Kết quả phân tích</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 md:space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2 text-sm md:text-base">Loại cây</h4>
                <p className="text-sm md:text-base text-gray-700 mb-1">
                  {analysisResult.plantType}
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-2 text-sm md:text-base">
                  Tình trạng
                </h4>
                <p className="text-sm md:text-base text-gray-700">{analysisResult.condition}</p>
              </div>
            </div>

            <div className="space-y-3 md:space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2 text-sm md:text-base">
                  Chẩn đoán chi tiết
                </h4>
                <p className="text-sm md:text-base text-gray-700">{analysisResult.diagnosis}</p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3 text-sm md:text-base">
                  Kế hoạch chăm sóc
                </h4>
                <ul className="space-y-2">
                  {analysisResult.treatments.map((treatment, index) => (
                    <li key={treatment.id} className="flex items-start gap-2">
                      <span className="text-green-600 mt-1 text-sm md:text-base">{index + 1}.</span>
                      <span className="text-xs md:text-base text-gray-700">{treatment.action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="pt-3 md:pt-4 border-t border-gray-200">
              <Button
                onClick={handleReset}
                variant="outline"
                className="w-full text-sm md:text-base"
              >
                Phân tích ảnh khác
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      {/* Camera Component */}
      {showCamera && (
        <CameraCapture onImageCapture={handleCameraCapture} onClose={() => setShowCamera(false)} />
      )}
    </div>
  );
}
