"use client";

import { Button } from "@/components/ui/button";
import { Camera, RotateCcw, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

interface CameraCaptureProps {
  onImageCapture: (imageDataUrl: string) => void;
  onClose: () => void;
}

export function CameraCapture({ onImageCapture, onClose }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [facingMode, setFacingMode] = useState<"user" | "environment">("environment");
  const [error, setError] = useState<string | null>(null);

  const startCamera = useCallback(async () => {
    try {
      setError(null);

      // Stop existing stream if any
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          aspectRatio: { ideal: 4/3 }
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setIsStreaming(true);
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      setError("Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập camera.");
    }
  }, [facingMode]);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!context) return;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to data URL
    const imageDataUrl = canvas.toDataURL("image/jpeg", 0.8);

    // Stop camera and call callback
    stopCamera();
    onImageCapture(imageDataUrl);
  }, [onImageCapture, stopCamera]);

  const switchCamera = useCallback(() => {
    setFacingMode(prev => prev === "user" ? "environment" : "user");
  }, []);

  const handleClose = useCallback(() => {
    stopCamera();
    onClose();
  }, [stopCamera, onClose]);

  // Start camera when component mounts
  useEffect(() => {
    if (typeof navigator !== "undefined" && navigator.mediaDevices) {
      startCamera();
    } else {
      setError("Camera không được hỗ trợ trên thiết bị này.");
    }

    return () => {
      stopCamera();
    };
  }, [startCamera, stopCamera]);

  // Restart camera when facing mode changes
  useEffect(() => {
    if (isStreaming) {
      startCamera();
    }
  }, [facingMode, startCamera, isStreaming]);

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-black/80 text-white">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleClose}
          className="text-white hover:bg-white/20"
        >
          <X className="h-5 w-5" />
        </Button>

        <h2 className="text-lg font-semibold">Chụp ảnh cây trồng</h2>

        <Button
          variant="ghost"
          size="sm"
          onClick={switchCamera}
          className="text-white hover:bg-white/20"
          disabled={!isStreaming}
        >
          <RotateCcw className="h-5 w-5" />
        </Button>
      </div>

      {/* Camera View */}
      <div className="flex-1 relative overflow-hidden">
        {error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-white p-6">
              <Camera className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">Lỗi camera</p>
              <p className="text-sm opacity-75">{error}</p>
              <Button
                onClick={startCamera}
                className="mt-4 bg-green-600 hover:bg-green-700"
              >
                Thử lại
              </Button>
            </div>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              className="w-full h-full object-cover"
              playsInline
              muted
            />

            {/* Camera Grid Overlay */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Rule of thirds grid */}
              <div className="w-full h-full relative">
                <div className="absolute top-1/3 left-0 right-0 h-px bg-white/30"></div>
                <div className="absolute top-2/3 left-0 right-0 h-px bg-white/30"></div>
                <div className="absolute left-1/3 top-0 bottom-0 w-px bg-white/30"></div>
                <div className="absolute left-2/3 top-0 bottom-0 w-px bg-white/30"></div>
              </div>

              {/* Center focus indicator */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className="w-16 h-16 border-2 border-white/50 rounded-full"></div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Controls */}
      <div className="bg-black/80 p-6">
        <div className="flex items-center justify-center">
          <Button
            onClick={capturePhoto}
            disabled={!isStreaming}
            className="w-16 h-16 rounded-full bg-white hover:bg-gray-200 text-black border-4 border-white"
          >
            <Camera className="h-8 w-8" />
          </Button>
        </div>

        {/* Instructions */}
        <div className="text-center mt-4">
          <p className="text-white/75 text-sm">
            Giữ thiết bị ổn định và đảm bảo cây trong khung hình
          </p>
        </div>
      </div>

      {/* Hidden canvas for photo capture */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
