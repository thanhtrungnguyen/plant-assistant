"use client";

import AppLayout from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import useGeneratePostcast from "../../hooks/useGeneratePostcast";
import { useState } from "react";
import { Mic, Download, Play, Pause, Volume2, MapPin, Loader2, X, Sparkles } from "lucide-react";

export default function PodcastPage() {
  const { audioUrl, loading, error, generate, download, cancel, clear } = useGeneratePostcast();
  const [selectedVoice, setSelectedVoice] = useState<string>("female");
  const [isPlaying, setIsPlaying] = useState(false);

  const voiceOptions = [
    { value: "female", label: "Giọng nữ chuẩn", description: "Giọng nữ tự nhiên, dễ nghe" },
    { value: "female_soft", label: "Giọng nữ nhẹ nhàng", description: "Giọng nữ dịu dàng, thư giãn" },
    { value: "female_energetic", label: "Giọng nữ năng động", description: "Giọng nữ sôi nổi, tràn đầy năng lượng" },
    { value: "male", label: "Giọng nam", description: "Giọng nam trầm ấm" }
  ];

  const onGenerate = async () => {
    try {
      await generate("a3f1d5e7-6a4b-4c39-8a27-f8c7f9d1e123", selectedVoice);
    } catch (err) {
      console.error(err);
    }
  };

  const togglePlay = () => {
    const audio = document.querySelector('audio') as HTMLAudioElement;
    if (audio) {
      if (isPlaying) {
        audio.pause();
      } else {
        audio.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <AppLayout title="AI Podcast" subtitle="Tạo podcast cá nhân hóa về chăm sóc cây trồng">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Header Section */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-green-100 to-blue-100 px-4 py-2 rounded-full">
            <Sparkles className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-green-700">AI Podcast Generator</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Tạo Podcast Cá Nhân</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Tạo podcast cá nhân hóa dựa trên vị trí của bạn, thời tiết hiện tại và danh sách cây trồng. 
            AI sẽ tạo nội dung phù hợp và chuyển đổi thành giọng nói tự nhiên.
          </p>
        </div>

        {/* Voice Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Volume2 className="h-5 w-5" />
              Chọn Giọng Nói
            </CardTitle>
            <CardDescription>
              Lựa chọn kiểu giọng nói cho podcast của bạn
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedVoice} onValueChange={setSelectedVoice}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Chọn giọng nói" />
              </SelectTrigger>
              <SelectContent>
                {voiceOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div className="flex flex-col items-start">
                      <span className="font-medium">{option.label}</span>
                      <span className="text-xs text-gray-500">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="mt-3 flex items-center gap-2 text-sm text-gray-600">
              <MapPin className="h-4 w-4" />
              <span>Podcast sẽ được tạo dựa trên vị trí hiện tại của bạn</span>
            </div>
          </CardContent>
        </Card>

        {/* Generation Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic className="h-5 w-5" />
              Tạo Podcast
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <Button
                onClick={onGenerate}
                disabled={loading}
                size="lg"
                className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
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
                  onClick={cancel}
                  variant="outline"
                  size="lg"
                >
                  <X className="h-4 w-4 mr-2" />
                  Hủy
                </Button>
              )}

              {audioUrl && (
                <Button
                  onClick={clear}
                  variant="outline"
                  size="lg"
                >
                  <X className="h-4 w-4 mr-2" />
                  Xóa
                </Button>
              )}
            </div>

            {/* Loading Progress */}
            {loading && (
              <div className="space-y-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gradient-to-r from-green-600 to-blue-600 h-2 rounded-full animate-pulse" style={{width: "60%"}}></div>
                </div>
                <p className="text-sm text-gray-600 text-center">Đang tạo nội dung và chuyển đổi giọng nói...</p>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600 font-medium">Lỗi:</p>
                <p className="text-red-700">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Audio Player */}
        {audioUrl && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-5 w-5" />
                Podcast Của Bạn
              </CardTitle>
              <CardDescription>
                Podcast đã được tạo thành công với giọng {voiceOptions.find(v => v.value === selectedVoice)?.label.toLowerCase()}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Custom Audio Player */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 space-y-4">
                <div className="flex items-center justify-center">
                  <Button
                    onClick={togglePlay}
                    size="lg"
                    className="rounded-full h-16 w-16 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                  >
                    {isPlaying ? (
                      <Pause className="h-8 w-8" />
                    ) : (
                      <Play className="h-8 w-8 ml-1" />
                    )}
                  </Button>
                </div>
                
                <audio
                  controls
                  src={audioUrl}
                  className="w-full"
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onEnded={() => setIsPlaying(false)}
                />
              </div>

              {/* Download Options */}
              <div className="flex items-center justify-center gap-4">
                <Button
                  onClick={() => download("my-plant-podcast.wav")}
                  variant="outline"
                  size="lg"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Tải xuống
                </Button>
                
                <a
                  href={audioUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center"
                >
                  <Button variant="ghost" size="lg">
                    Mở trong tab mới
                  </Button>
                </a>
              </div>

              {/* Audio Info */}
              <div className="flex justify-center">
                <Badge variant="secondary" className="text-xs">
                  Giọng nói: {voiceOptions.find(v => v.value === selectedVoice)?.label}
                </Badge>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
