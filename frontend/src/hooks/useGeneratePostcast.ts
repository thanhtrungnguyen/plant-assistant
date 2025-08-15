"use client";
import { useCallback, useEffect, useRef, useState } from "react";

type LatLng = {
  latitude: number;
  longitude: number;
  accuracy: number;
  altitude?: number | null;
  altitudeAccuracy?: number | null;
  heading?: number | null;
  speed?: number | null;
  timestamp: number;
};

export type GeneratePodcastInput = {
  user_id: string;
  location?: {
    latitude: number;
    longitude: number;
    accuracy: number;
    altitude?: number | null;
    altitudeAccuracy?: number | null;
    heading?: number | null;
    speed?: number | null;
    timestamp: number;
  };
  voice_type?: "female" | "male" | "female_soft" | "female_energetic";
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5000";

export async function requestPostcast(input: GeneratePodcastInput): Promise<Blob> {
  const res = await fetch(`${API_BASE}/podcast/generate_podcast`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error(`Request failed ${res.status}: ${t}`);
  }

  // Backend trả về bytes WAV
  return await res.blob();
}

async function getCurrentLatLng(timeoutMs = 5000): Promise<LatLng | null> {
  if (typeof navigator === "undefined" || !navigator.geolocation) return null;
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (p) => resolve({
        latitude: p.coords.latitude,
        longitude: p.coords.longitude,
        accuracy: p.coords.accuracy,
        altitude: p.coords.altitude,
        altitudeAccuracy: p.coords.altitudeAccuracy,
        heading: p.coords.heading,
        speed: p.coords.speed,
        timestamp: p.timestamp
      }),
      () => resolve(null),
      { timeout: timeoutMs },
    );
  });
}

export default function useGeneratePostcast() {
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
    async (userId: string, voiceType: string = "female", geoTimeoutMs = 5000) => {
      try {
        setError(null);
        setLoading(true);
        abortRef.current?.abort();
        abortRef.current = new AbortController();

        const loc = await getCurrentLatLng(geoTimeoutMs);

        const payload: GeneratePodcastInput = {
          user_id: userId,
          location: loc ?? undefined, // nếu không lấy được thì backend sẽ dùng address mặc định
          voice_type: voiceType as "female" | "male" | "female_soft" | "female_energetic",
        };

        const blob = await requestPostcast(payload);
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
