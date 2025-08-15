"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { Eye, EyeOff, Leaf, LogIn, Mail, User } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [name, setName] = React.useState("");
  const [showPassword, setShowPassword] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const r = await api("/auth/register", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email, password, name }),
      });
      if (!r.ok) throw new Error("Đăng ký thất bại");
      router.push("/login");
    } catch (err: any) {
      setError(err.message || "Đăng ký thất bại");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50 flex items-center justify-center">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-0 w-72 h-72 bg-green-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute top-0 right-0 w-72 h-72 bg-emerald-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-teal-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      {/* Main content - Centered */}
      <div className="relative w-full max-w-md mx-auto px-6 py-12">
        {/* Logo */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg">
              <Leaf className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Plant Assistant</h1>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-white/20">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Tạo tài khoản mới</h2>
            <p className="text-sm text-gray-600">
              Tham gia cùng chúng tôi trong hành trình chăm sóc cây xanh
            </p>
          </div>

              <form onSubmit={onSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-gray-700 font-medium">
                    Họ và tên
                  </Label>
                  <div className="relative">
                    <Input
                      id="name"
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="pl-10 h-12 border-gray-200 focus:border-green-500 focus:ring-green-500"
                      placeholder="Nhập họ và tên"
                      required
                    />
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-gray-700 font-medium">
                    Email
                  </Label>
                  <div className="relative">
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10 h-12 border-gray-200 focus:border-green-500 focus:ring-green-500"
                      placeholder="Nhập email của bạn"
                      required
                    />
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-gray-700 font-medium">
                    Mật khẩu
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10 h-12 border-gray-200 focus:border-green-500 focus:ring-green-500"
                      placeholder="Tạo mật khẩu mạnh"
                      required
                    />
                    <LogIn className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Mật khẩu nên có ít nhất 8 ký tự
                  </p>
                </div>

                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}

                <Button
                  type="submit"
                  className="w-full h-12 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium rounded-lg shadow-lg transition-all duration-200 transform hover:scale-[1.02]"
                  disabled={loading}
                >
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Đang tạo tài khoản...
                    </div>
                  ) : (
                    "Tạo tài khoản"
                  )}
                </Button>
              </form>

              <div className="mt-6">
                <p className="text-xs text-gray-500 text-center leading-relaxed">
                  Bằng việc đăng ký, bạn đồng ý với{" "}
                  <a href="#" className="text-green-600 hover:text-green-500">
                    Điều khoản sử dụng
                  </a>{" "}
                  và{" "}
                  <a href="#" className="text-green-600 hover:text-green-500">
                    Chính sách bảo mật
                  </a>{" "}
                  của chúng tôi.
                </p>
              </div>

              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  Đã có tài khoản?{" "}
                  <a
                    href="/login"
                    className="font-medium text-green-600 hover:text-green-500 transition-colors"
                  >
                    Đăng nhập ngay
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
  );
}
