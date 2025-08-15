"use client";

import AppLayout from "@/components/layout/AppLayout";
import useGeneratePostcast from "../../hooks/useGeneratePostcast";

export default function PodcastPage() {
  const { audioUrl, loading, error, generate, download, cancel, clear } = useGeneratePostcast();

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
      <div className="max-w-3xl mx-auto p-6 space-y-4">
        <h2 className="text-lg font-semibold">Tạo Podcast</h2>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onGenerate}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50"
          >
            {loading ? "Đang tạo..." : "Tạo podcast"}
          </button>

          {loading && (
            <button
              type="button"
              onClick={() => cancel()}
              className="px-3 py-2 bg-yellow-500 text-white rounded"
            >
              Hủy
            </button>
          )}

          {audioUrl && (
            <button
              type="button"
              onClick={() => clear()}
              className="px-3 py-2 bg-gray-200 text-gray-800 rounded"
            >
              Xóa kết quả
            </button>
          )}
        </div>

        {error && <div className="text-red-600">{error}</div>}

        {audioUrl && (
          <div className="mt-4">
            <h3 className="font-medium mb-2">Kết quả</h3>
            <audio
              ref={(el) => {
                if (el) {
                  el.playbackRate = 1.25;
                }
              }}
              controls
              src={audioUrl}
              className="w-full"
            />
            <div className="mt-2 flex items-center gap-4">
              <a
                href={audioUrl}
                download="podcast.wav"
                target="_blank"
                rel="noreferrer"
                className="text-green-600"
              >
                Mở / Tải file audio
              </a>
              <button
                type="button"
                onClick={() => download("podcast.wav")}
                className="px-2 py-1 bg-gray-100 rounded text-sm"
              >
                Tải xuống
              </button>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
