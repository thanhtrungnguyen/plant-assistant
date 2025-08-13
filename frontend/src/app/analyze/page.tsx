import AppLayout from "@/components/layout/AppLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PlantAnalyzer } from "@/components/ui/plant-analyzer";
import { Brain, Leaf, Search, TrendingUp } from "lucide-react";

export default function AnalyzePage() {
  return (
    <AppLayout title="Phân tích cây trồng" subtitle="Sử dụng công nghệ AI để phân tích tình trạng sức khỏe của cây trồng từ hình ảnh">
      <div className="space-y-6 md:space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
          <Card>
            <CardHeader className="text-center p-4 md:p-6">
              <div className="mx-auto w-10 h-10 md:w-12 md:h-12 bg-green-100 rounded-full flex items-center justify-center mb-2">
                <Search className="w-5 h-5 md:w-6 md:h-6 text-green-600" />
              </div>
              <CardTitle className="text-base md:text-lg">Tải ảnh lên</CardTitle>
              <CardDescription className="text-sm">
                Chụp hoặc tải lên hình ảnh cây trồng của bạn
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="text-center p-4 md:p-6">
              <div className="mx-auto w-10 h-10 md:w-12 md:h-12 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                <Brain className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
              </div>
              <CardTitle className="text-base md:text-lg">AI phân tích</CardTitle>
              <CardDescription className="text-sm">
                AI sẽ nhận dạng loại cây và đánh giá tình trạng sức khỏe
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="text-center p-4 md:p-6">
              <div className="mx-auto w-10 h-10 md:w-12 md:h-12 bg-emerald-100 rounded-full flex items-center justify-center mb-2">
                <TrendingUp className="w-5 h-5 md:w-6 md:h-6 text-emerald-600" />
              </div>
              <CardTitle className="text-base md:text-lg">Nhận kết quả</CardTitle>
              <CardDescription className="text-sm">
                Nhận được khuyến nghị chăm sóc chi tiết
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        <PlantAnalyzer />

        <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
          <CardHeader className="p-4 md:p-6">
            <CardTitle className="flex items-center gap-2 text-green-800 text-base md:text-lg">
              <Leaf className="w-4 h-4 md:w-5 md:h-5" />
              Mẹo để có kết quả phân tích tốt nhất
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-green-700 p-4 md:p-6 pt-0">
            <div className="flex items-start gap-2">
              <span className="text-green-600 mt-1">•</span>
              <span className="text-sm md:text-base">Chụp ảnh trong điều kiện ánh sáng tự nhiên</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 mt-1">•</span>
              <span className="text-sm md:text-base">Đảm bảo cây nằm trong khung hình một cách rõ ràng</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 mt-1">•</span>
              <span className="text-sm md:text-base">Chụp từ nhiều góc độ khác nhau để có đánh giá toàn diện</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 mt-1">•</span>
              <span className="text-sm md:text-base">Tập trung vào lá cây để AI có thể phân tích tình trạng sức khỏe</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
