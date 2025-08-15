"use client";

import AppLayout from "@/components/layout/AppLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, MapPin, Mic, MicOff, Play, Square, Trash2, Volume2 } from "lucide-react";
import useGeneratePodcast from "../../hooks/useGeneratePodcast";

export default function PodcastPage() {
  const { audioUrl, loading, error, generate, download, cancel, clear } = useGeneratePodcast();

  const onGenerate = async () => {
    try {
      // TODO: thay 'demo-user-001' bằng userId thực tế của bạn
      await generate("a3f1d5e7-6a4b-4c39-8a27-f8c7f9d1e123"); // hook sẽ tự lấy geolocation rồi gọi API
    } catch (err) {
      // error đã được quản lý trong hook (state `error`)
      console.error(err);
    }
  };

  return (
    <AppLayout title="Podcast" subtitle="Tạo podcast theo vị trí hiện tại">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Header Card */}
        <Card className="bg-gradient-to-br from-green-50 to-blue-50 border-green-200">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2 text-2xl">
              <Volume2 className="h-8 w-8 text-green-600" />
              Tạo Podcast Thông Minh
            </CardTitle>
            <CardDescription className="text-base">
              Tạo podcast tự động dựa trên vị trí hiện tại của bạn với AI
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Main Content Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-blue-600" />
              Tạo Podcast Theo Vị Trí
            </CardTitle>
            <CardDescription>
              Ứng dụng sẽ sử dụng vị trí hiện tại để tạo nội dung podcast phù hợp
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3">
              <Button
                onClick={onGenerate}
                disabled={loading}
                size="lg"
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                {loading ? (
                  <>
                    <MicOff className="h-4 w-4 mr-2 animate-pulse" />
                    Đang tạo...
                  </>
                ) : (
                  <>
                    <Mic className="h-4 w-4 mr-2" />
                    Tạo Podcast
                  </>
                )}
              </Button>

              {loading && (
                <Button
                  onClick={() => cancel()}
                  variant="outline"
                  size="lg"
                  className="border-yellow-300 text-yellow-700 hover:bg-yellow-50"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Hủy
                </Button>
              )}

              {audioUrl && (
                <Button
                  onClick={() => clear()}
                  variant="outline"
                  size="lg"
                  className="border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Xóa kết quả
                </Button>
              )}
            </div>

            {/* Loading State */}
            {loading && (
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-center space-x-3">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <div className="text-blue-700 font-medium">
                      Đang phân tích vị trí và tạo nội dung podcast...
                    </div>
                  </div>
                  <div className="mt-4 text-center text-sm text-blue-600">
                    Quá trình này có thể mất vài phút
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Error State */}
            {error && (
              <Card className="bg-red-50 border-red-200">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 text-red-700">
                    <div className="h-2 w-2 bg-red-500 rounded-full"></div>
                    <span className="font-medium">Có lỗi xảy ra:</span>
                  </div>
                  <p className="mt-2 text-red-600">{error}</p>
                </CardContent>
              </Card>
            )}

            {/* Success State - Audio Player */}
            {audioUrl && (
              <Card className="bg-green-50 border-green-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-800">
                    <Play className="h-5 w-5" />
                    Podcast đã sẵn sàng!
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Audio chất lượng cao
                    </Badge>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      Tốc độ 1.25x
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <audio
                    ref={(el) => {
                      if (el) {
                        el.playbackRate = 1.25;
                      }
                    }}
                    controls
                    src={audioUrl}
                    className="w-full h-12 rounded-lg"
                    style={{
                      backgroundColor: '#f9fafb',
                      border: '1px solid #e5e7eb'
                    }}
                  />

                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <Button
                      asChild
                      variant="outline"
                      className="border-green-300 text-green-700 hover:bg-green-50"
                    >
                      <a
                        href={audioUrl}
                        download="podcast.wav"
                        target="_blank"
                        rel="noreferrer"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Tải xuống file
                      </a>
                    </Button>

                    <Button
                      onClick={() => download("plant-assistant-podcast.wav")}
                      variant="outline"
                      className="border-blue-300 text-blue-700 hover:bg-blue-50"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Lưu với tên mới
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="pt-6">
            <div className="text-center text-sm text-gray-600">
              <p className="mb-2">
                <strong>Mẹo:</strong> Podcast được tạo dựa trên vị trí hiện tại và thông tin môi trường xung quanh
              </p>
              <p>
                Đảm bảo bạn đã cấp quyền truy cập vị trí cho trình duyệt để có kết quả tốt nhất
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
