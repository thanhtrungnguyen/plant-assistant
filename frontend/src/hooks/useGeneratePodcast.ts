"use client";
import { api } from "@/lib/api";
import { useCallback, useEffect, useRef, useState } from "react";

type LatLng = { latitude: number; longitude: number };

export type GeneratePodcastInput = {
  location?: {
    latitude: number;
    longitude: number;
  };
};

export async function requestPodcast(input: GeneratePodcastInput): Promise<Blob> {
  const response = await api("/podcast/generate_podcast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "");
    throw new Error(`Request failed ${response.status}: ${errorText}`);
  }

  // Backend trả về bytes WAV
  return await response.blob();
}

async function getCurrentLatLng(timeoutMs = 5000): Promise<LatLng | null> {
  if (typeof navigator === "undefined" || !navigator.geolocation) return null;
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (p) => resolve({ latitude: p.coords.latitude, longitude: p.coords.longitude }),
      () => resolve(null),
      { timeout: timeoutMs },
    );
  });
}

export default function useGeneratePodcast() {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      abortRef.current?.abort();
    };
  }, [audioUrl]);

  const clear = useCallback(() => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setError(null);
  }, [audioUrl]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const download = useCallback(
    (filename = "podcast.wav") => {
      if (!audioUrl) return;
      const a = document.createElement("a");
      a.href = audioUrl;
      a.download = filename;
      a.click();
    },
    [audioUrl],
  );

  const generate = useCallback(
    async (geoTimeoutMs = 5000) => {
      try {
        setError(null);
        setLoading(true);
        abortRef.current?.abort();
        abortRef.current = new AbortController();

        const loc = await getCurrentLatLng(geoTimeoutMs);

        const payload: GeneratePodcastInput = {
          location: loc ?? undefined, // nếu không lấy được thì backend sẽ dùng address mặc định
        };

        const blob = await requestPodcast(payload);
        const url = URL.createObjectURL(blob);
        if (audioUrl) URL.revokeObjectURL(audioUrl);
        setAudioUrl(url);

        return url;
      } catch (e: any) {
        if (e?.name === "AbortError") return;
        setError(e?.message ?? "Failed to generate podcast");
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [audioUrl],
  );

  return {
    audioUrl,
    loading,
    error,
    generate,
    download,
    cancel,
    clear,
  };
}
