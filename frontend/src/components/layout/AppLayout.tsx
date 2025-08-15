"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
    Bell,
    Calendar,
    CheckSquare,
    ChevronDown,
    Leaf,
    LogOut,
    Menu,
    MessageSquare,
    Search,
    Settings,
    User,
    X
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React, { useEffect, useState } from "react";

interface NavigationItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

const navigationItems: NavigationItem[] = [
  {
    href: "/chatbot",
    label: "Plant AI",
    icon: MessageSquare,
    description: "Trợ lý AI",
  },
  {
    href: "/calendar",
    label: "Lịch chăm sóc",
    icon: Calendar,
    description: "Lịch trình",
  },
  {
    href: "/tasks",
    label: "Nhiệm vụ",
    icon: CheckSquare,
    description: "Quản lý tasks",
  },
  {
    href: "/analyze",
    label: "Phân tích ảnh",
    icon: Search,
    description: "AI phân tích",
  },
];

interface User {
  name: string;
  email: string;
  avatar?: string;
  plantsCount: number;
}

// Mock user data - replace with real user data
const mockUser: User = {
  name: "Nguyễn Văn A",
  email: "nguyenvana@example.com",
  avatar: undefined,
  plantsCount: 15,
};

interface AppLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  showNavigation?: boolean;
}

export default function AppLayout({
  children,
  title,
  subtitle,
  showNavigation = true,
}: AppLayoutProps) {
  const pathname = usePathname();
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Handle mobile detection
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setShowMobileMenu(false);
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    window.location.href = "/login";
  };

  const toggleMobileMenu = () => {
    setShowMobileMenu(!showMobileMenu);
  };

  return (
    <div className="min-h-screen bg-gray-50 max-w-full">
      {/* Header - Hidden on mobile */}
      <header className="hidden lg:block bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left side - Logo and Title */}
            <div className="flex items-center gap-4">
              {/* Logo */}
              <Link href="/chatbot" className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Leaf className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Plant Assistant</h1>
                </div>
              </Link>

              {/* Page title */}
              {title && (
                <div>
                  <div className="flex items-center gap-2 text-gray-500">
                    <span>/</span>
                    <span className="text-gray-900 font-medium">{title}</span>
                  </div>
                  {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
                </div>
              )}
            </div>

            {/* Center - Navigation (desktop only) */}
            {showNavigation && (
              <nav className="hidden lg:flex items-center gap-1">
                {navigationItems.map((item) => {
                  const isActive = pathname === item.href;
                  const Icon = item.icon;

                  return (
                    <Link key={item.href} href={item.href}>
                      <Button
                        variant={isActive ? "default" : "ghost"}
                        size="sm"
                        className={`flex items-center gap-2 ${
                          isActive
                            ? "bg-green-600 hover:bg-green-700 text-white"
                            : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                        <span className="hidden xl:inline">{item.label}</span>
                      </Button>
                    </Link>
                  );
                })}
              </nav>
            )}

            {/* Right side - User actions */}
            <div className="flex items-center gap-3">
              {/* Notifications */}
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative"
                >
                  <Bell className="h-5 w-5" />
                  <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs flex items-center justify-center">
                    <span className="sr-only">2 notifications</span>
                  </span>
                </Button>

                {/* Notifications dropdown */}
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <h3 className="font-semibold text-gray-900">Thông báo</h3>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      <div className="px-4 py-3 hover:bg-gray-50 border-b border-gray-50">
                        <p className="text-sm font-medium text-gray-900">Pothos cần tưới nước</p>
                        <p className="text-xs text-gray-500 mt-1">2 giờ trước</p>
                      </div>
                      <div className="px-4 py-3 hover:bg-gray-50">
                        <p className="text-sm font-medium text-gray-900">
                          Monstera đã sẵn sàng bón phân
                        </p>
                        <p className="text-xs text-gray-500 mt-1">1 ngày trước</p>
                      </div>
                    </div>
                    <div className="px-4 py-2 border-t border-gray-100">
                      <Button variant="ghost" size="sm" className="w-full text-blue-600">
                        Xem tất cả thông báo
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* User Profile */}
              <div className="relative">
                <Button
                  variant="ghost"
                  onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                  className="flex items-center gap-3 hover:bg-gray-100 p-2"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={mockUser.avatar} alt={mockUser.name} />
                    <AvatarFallback className="bg-green-100 text-green-600">
                      {mockUser.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")
                        .slice(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-medium text-gray-900">{mockUser.name}</p>
                    <p className="text-xs text-gray-500">{mockUser.plantsCount} cây trồng</p>
                  </div>
                  <ChevronDown className="h-4 w-4 text-gray-500" />
                </Button>

                {/* Profile dropdown */}
                {showProfileDropdown && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                    {/* User info */}
                    <div className="px-4 py-3 border-b border-gray-100">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={mockUser.avatar} alt={mockUser.name} />
                          <AvatarFallback className="bg-green-100 text-green-600">
                            {mockUser.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")
                              .slice(0, 2)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-gray-900">{mockUser.name}</p>
                          <p className="text-sm text-gray-500">{mockUser.email}</p>
                        </div>
                      </div>
                    </div>

                    {/* Quick stats */}
                    <div className="px-4 py-3 border-b border-gray-100">
                      <div className="grid grid-cols-2 gap-4 text-center">
                        <div>
                          <p className="text-lg font-bold text-green-600">{mockUser.plantsCount}</p>
                          <p className="text-xs text-gray-500">Cây trồng</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-blue-600">3</p>
                          <p className="text-xs text-gray-500">Cần chăm sóc</p>
                        </div>
                      </div>
                    </div>

                    {/* Menu items */}
                    <div className="py-1">
                      <Link href="/profile">
                        <Button variant="ghost" className="w-full justify-start px-4 py-2">
                          <User className="h-4 w-4 mr-3" />
                          Hồ sơ cá nhân
                        </Button>
                      </Link>
                      <Link href="/settings">
                        <Button variant="ghost" className="w-full justify-start px-4 py-2">
                          <Settings className="h-4 w-4 mr-3" />
                          Cài đặt
                        </Button>
                      </Link>
                    </div>

                    <div className="border-t border-gray-100 pt-1">
                      <Button
                        variant="ghost"
                        onClick={handleLogout}
                        className="w-full justify-start px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <LogOut className="h-4 w-4 mr-3" />
                        Đăng xuất
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Button - Only visible on mobile */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button
          variant="outline"
          size="sm"
          onClick={toggleMobileMenu}
          className="bg-white shadow-md"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      {/* Mobile Navigation Sidebar */}
      {showMobileMenu && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50"
            onClick={() => setShowMobileMenu(false)}
          />

          {/* Sidebar */}
          <div className="fixed left-0 top-0 h-full w-80 bg-white shadow-xl">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Leaf className="h-6 w-6 text-green-600" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Plant Assistant</h1>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowMobileMenu(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            {/* Mobile Navigation */}
            <nav className="p-4">
              <div className="space-y-2">
                {navigationItems.map((item) => {
                  const isActive = pathname === item.href;
                  const Icon = item.icon;

                  return (
                    <Link key={item.href} href={item.href} onClick={() => setShowMobileMenu(false)}>
                      <div
                        className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                          isActive
                            ? "bg-green-100 text-green-700"
                            : "text-gray-600 hover:bg-gray-100"
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                        <div>
                          <p className="font-medium">{item.label}</p>
                          <p className="text-xs text-gray-500">{item.description}</p>
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </nav>

            {/* Mobile User Section */}
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center gap-3 mb-3">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={mockUser.avatar} alt={mockUser.name} />
                  <AvatarFallback className="bg-green-100 text-green-600">
                    {mockUser.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium text-gray-900">{mockUser.name}</p>
                  <p className="text-sm text-gray-500">{mockUser.plantsCount} cây trồng</p>
                </div>
              </div>

              <div className="flex gap-2">
                <Link href="/profile" className="flex-1">
                  <Button variant="outline" size="sm" className="w-full">
                    <User className="h-4 w-4 mr-2" />
                    Hồ sơ
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  className="text-red-600 border-red-200 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:pt-6 pt-16">{children}</main>
    </div>
  );
}
