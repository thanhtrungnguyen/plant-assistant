const API = process.env.NEXT_PUBLIC_API_BASE_URL!;

// Debug environment variable
console.log("🔧 API Base URL:", API);
console.log("🔧 Environment Variables:", {
  NODE_ENV: process.env.NODE_ENV,
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL
});

export async function api(path: string, init: RequestInit = {}) {
  const fullUrl = API + path;

  console.log(`🚀 API Request: ${init.method || "GET"} ${fullUrl}`);
  if (init.body) {
    console.log("📤 Request body:", init.body);
  }

  // Always include cookies
  let res = await fetch(fullUrl, { ...init, credentials: "include" });

  console.log(`📥 API Response: ${res.status} ${res.statusText} for ${fullUrl}`);

  if (res.status !== 401) {
    // Log response for debugging
    if (!res.ok) {
      try {
        const errorText = await res.clone().text();
        console.error("❌ API Error response:", errorText);
      } catch (e) {
        console.error("❌ Failed to read error response");
      }
    }
    return res;
  }

  console.log("🔄 Attempting token refresh...");

  // Try one refresh
  const refreshUrl = API + "/auth/refresh";
  console.log(`🔄 Refresh request: POST ${refreshUrl}`);

  const r = await fetch(refreshUrl, {
    method: "POST",
    credentials: "include",
  });

  console.log(`🔄 Refresh response: ${r.status} ${r.statusText}`);

  if (!r.ok) {
    console.warn("⚠️ Token refresh failed, returning original response");
    return res;
  }

  console.log("✅ Token refreshed, retrying original request...");

  // Retry original
  const retryRes = await fetch(fullUrl, { ...init, credentials: "include" });
  console.log(`🔄 Retry response: ${retryRes.status} ${retryRes.statusText}`);

  return retryRes;
}
