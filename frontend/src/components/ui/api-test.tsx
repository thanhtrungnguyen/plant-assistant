"use client";

import { chatApi } from "@/lib/chat-api";
import { useState } from "react";

export function ApiTest() {
  const [testResult, setTestResult] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const testConnection = async () => {
    setIsLoading(true);
    setTestResult("");

    try {
      const result = await chatApi.testConnection();
      setTestResult(JSON.stringify(result, null, 2));
    } catch (error) {
      setTestResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  const testMessage = async () => {
    setIsLoading(true);
    setTestResult("");

    try {
      const result = await chatApi.testMessage("Xin chào bot!");
      setTestResult(JSON.stringify(result, null, 2));
    } catch (error) {
      setTestResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 border border-gray-300 rounded-lg bg-gray-50">
      <h3 className="font-bold mb-3">API Test Panel</h3>

      <div className="space-x-2 mb-3">
        <button
          onClick={testConnection}
          disabled={isLoading}
          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Test Connection
        </button>

        <button
          onClick={testMessage}
          disabled={isLoading}
          className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          Test Message
        </button>
      </div>

      {isLoading && <div className="text-blue-600">Loading...</div>}

      {testResult && (
        <pre className="mt-3 p-2 bg-white border rounded text-xs overflow-auto max-h-40">
          {testResult}
        </pre>
      )}
    </div>
  );
}
