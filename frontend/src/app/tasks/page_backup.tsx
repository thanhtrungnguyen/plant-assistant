"use client";

import AppLayout from "@/components/layout/AppLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  AlertCircle,
  Calendar,
  CheckCircle,
  Droplets,
  Plus,
  RotateCcw,
  Scissors,
  Sprout,
} from "lucide-react";
import { useState } from "react";

interface Task {
  id: string;
  title: string;
  description?: string;
  dueDate: Date;
  type: "watering" | "fertilizing" | "pruning" | "repotting";
  plantName: string;
  completed: boolean;
  priority: "low" | "medium" | "high";
  createdAt: Date;
}

const mockTasks: Task[] = [
  {
    id: "1",
    title: "Tưới nước cho Pothos",
    description: "Kiểm tra độ ẩm đất trước khi tưới",
    dueDate: new Date(2025, 7, 11),
    type: "watering",
    plantName: "Pothos của tôi",
    completed: false,
    priority: "high",
    createdAt: new Date(2025, 7, 8),
  },
  {
    id: "2",
    title: "Bón phân cho Monstera",
    description: "Sử dụng phân NPK pha loãng",
    dueDate: new Date(2025, 7, 12),
    type: "fertilizing",
    plantName: "Monstera xinh đẹp",
    completed: false,
    priority: "medium",
    createdAt: new Date(2025, 7, 9),
  },
];

export default function TasksPage() {
  const [tasks] = useState<Task[]>(mockTasks);

  const getTaskIcon = (type: Task["type"]) => {
    switch (type) {
      case "watering":
        return <Droplets className="h-4 w-4 text-blue-500" />;
      case "fertilizing":
        return <Sprout className="h-4 w-4 text-green-500" />;
      case "pruning":
        return <Scissors className="h-4 w-4 text-orange-500" />;
      case "repotting":
        return <RotateCcw className="h-4 w-4 text-purple-500" />;
    }
  };

  const getPriorityColor = (priority: Task["priority"]) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-green-100 text-green-800 border-green-200";
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(date);
  };

  const isOverdue = (dueDate: Date) => {
    return dueDate < new Date() && dueDate.toDateString() !== new Date().toDateString();
  };

  return (
    <AppLayout
      title="Quản lý nhiệm vụ"
      subtitle="Theo dõi và quản lý tất cả nhiệm vụ chăm sóc cây trồng"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <Button className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            Thêm nhiệm vụ
          </Button>
        </div>

        {/* Tasks List */}
        <Card>
          <CardContent className="p-4 md:p-6">
            <div className="space-y-4">
              {tasks.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Không có nhiệm vụ nào</p>
                </div>
              ) : (
                tasks.map((task) => {
                  const overdueTask = isOverdue(task.dueDate);

                  return (
                    <div
                      key={task.id}
                      className={`p-4 rounded-lg border transition-colors ${
                        task.completed
                          ? "bg-gray-50 border-gray-200"
                          : overdueTask
                            ? "bg-red-50 border-red-200"
                            : "bg-white border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                {getTaskIcon(task.type)}
                                <h3
                                  className={`font-semibold ${
                                    task.completed ? "line-through text-gray-500" : "text-gray-900"
                                  }`}
                                >
                                  {task.title}
                                </h3>
                              </div>

                              <p className="text-sm text-gray-600 mb-2">{task.plantName}</p>

                              {task.description && (
                                <p className="text-sm text-gray-500 mb-3">{task.description}</p>
                              )}

                              <div className="flex items-center gap-2 text-sm">
                                <Calendar className="h-4 w-4 text-gray-400" />
                                <span
                                  className={`${
                                    overdueTask ? "text-red-600 font-medium" : "text-gray-500"
                                  }`}
                                >
                                  {formatDate(task.dueDate)}
                                </span>
                                {overdueTask && <AlertCircle className="h-4 w-4 text-red-500" />}
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              <Badge className={getPriorityColor(task.priority)}>
                                {task.priority === "high"
                                  ? "Cao"
                                  : task.priority === "medium"
                                    ? "Trung bình"
                                    : "Thấp"}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
