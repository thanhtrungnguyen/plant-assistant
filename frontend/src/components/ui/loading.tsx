import { Leaf } from "lucide-react";

export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="flex items-center gap-3 mb-4">
        <div className="bg-green-100 p-3 rounded-full animate-pulse">
          <Leaf className="w-8 h-8 text-green-600" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-semibold text-gray-800">Plant Assistant</h2>
          <p className="text-gray-600">Đang tải...</p>
        </div>
      </div>

      <div className="flex space-x-2">
        <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce"></div>
        <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
    </div>
  );
}

export function PageLoader({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {children}
    </div>
  );
}
