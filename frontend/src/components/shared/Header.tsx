"use client";

import { Button } from "@/components/ui/button";
import { Bell, Calendar, CheckSquare, Home, Leaf, MessageSquare, Search, User } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigationItems = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: Home,
  },
  {
    href: "/chatbot",
    label: "Plant AI",
    icon: MessageSquare,
  },
  {
    href: "/calendar",
    label: "Lịch",
    icon: Calendar,
  },
  {
    href: "/tasks",
    label: "Nhiệm vụ",
    icon: CheckSquare,
  },
  {
    href: "/analyze",
    label: "Phân tích",
    icon: Search,
  },
];

interface HeaderProps {
  title?: string;
  subtitle?: string;
  showNavigation?: boolean;
}

export default function Header({ title, subtitle, showNavigation = true }: HeaderProps) {
  const pathname = usePathname();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Leaf className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Plant Assistant</h1>
            </div>
          </Link>

          {/* Navigation */}
          {showNavigation && (
            <nav className="hidden md:flex items-center gap-1">
              {navigationItems.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;

                return (
                  <Link key={item.href} href={item.href}>
                    <Button
                      variant={isActive ? "default" : "ghost"}
                      size="sm"
                      className={isActive ? "bg-green-600 hover:bg-green-700 text-white" : ""}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.label}
                    </Button>
                  </Link>
                );
              })}
            </nav>
          )}

          {/* User Profile */}
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm">
              <Bell className="h-5 w-5" />
            </Button>

            <div className="flex items-center gap-2">
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-green-600" />
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium">Nguyễn Văn A</p>
                <p className="text-xs text-gray-500">15 cây trồng</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {showNavigation && (
        <div className="md:hidden border-t border-gray-200 bg-gray-50">
          <div className="px-4 py-2">
            <div className="flex gap-1 overflow-x-auto">
              {navigationItems.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;

                return (
                  <Link key={item.href} href={item.href}>
                    <Button
                      variant={isActive ? "default" : "ghost"}
                      size="sm"
                      className={`whitespace-nowrap ${isActive ? "bg-green-600 text-white" : ""}`}
                    >
                      <Icon className="h-4 w-4 mr-1" />
                      {item.label}
                    </Button>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
