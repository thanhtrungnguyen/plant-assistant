'use client';

import AppLayout from "@/components/layout/AppLayout";
import { AlertCircle, Calendar as CalendarIcon, CheckCircle, Clock } from 'lucide-react';
import { useState } from 'react';

interface Event {
  id: string;
  title: string;
  plant: string;
  date: Date;
  type: 'watering' | 'fertilizing' | 'pruning' | 'repotting';
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
}

const mockEvents: Event[] = [
  {
    id: '1',
    title: 'Tưới nước',
    plant: 'Pothos của tôi',
    date: new Date(2025, 0, 10),
    type: 'watering',
    completed: false,
    priority: 'high'
  },
  {
    id: '2',
    title: 'Bón phân',
    plant: 'Monstera xinh đẹp',
    date: new Date(2025, 0, 12),
    type: 'fertilizing',
    completed: false,
    priority: 'medium'
  }
];

export default function CalendarPage() {
  const [events] = useState<Event[]>(mockEvents);

  const formatDate = (date: Date) => {
    const today = new Date();
    if (date.toDateString() === today.toDateString()) {
      return 'Hôm nay';
    } else {
      return date.toLocaleDateString('vi-VN', {
        weekday: 'long',
        month: 'long',
        day: 'numeric'
      });
    }
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'watering': return 'bg-blue-100 text-blue-800';
      case 'fertilizing': return 'bg-green-100 text-green-800';
      case 'pruning': return 'bg-yellow-100 text-yellow-800';
      case 'repotting': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const upcomingEvents = events
    .filter(event => event.date >= new Date() && !event.completed)
    .sort((a, b) => a.date.getTime() - b.date.getTime());

  return (
    <AppLayout title="Lịch chăm sóc" subtitle="Quản lý lịch trình chăm sóc tất cả cây trồng của bạn">
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sắp tới</p>
                <p className="text-xl md:text-2xl font-bold text-gray-900">{upcomingEvents.length}</p>
              </div>
              <CalendarIcon className="w-6 h-6 md:w-8 md:h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Hôm nay</p>
                <p className="text-xl md:text-2xl font-bold text-gray-900">
                  {events.filter(e => e.date.toDateString() === new Date().toDateString()).length}
                </p>
              </div>
              <Clock className="w-6 h-6 md:w-8 md:h-8 text-orange-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Hoàn thành</p>
                <p className="text-xl md:text-2xl font-bold text-gray-900">
                  {events.filter(e => e.completed).length}
                </p>
              </div>
              <CheckCircle className="w-6 h-6 md:w-8 md:h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Quá hạn</p>
                <p className="text-xl md:text-2xl font-bold text-gray-900">
                  {events.filter(e => e.date < new Date() && !e.completed).length}
                </p>
              </div>
              <AlertCircle className="w-6 h-6 md:w-8 md:h-8 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
          <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-4">
            Sự kiện sắp tới
          </h2>

          <div className="space-y-4">
            {upcomingEvents.length === 0 ? (
              <div className="text-center py-8">
                <CalendarIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Không có sự kiện nào sắp tới</p>
              </div>
            ) : (
              upcomingEvents.map((event) => (
                <div key={event.id} className="border-l-4 border-blue-500 bg-gray-50 p-4 rounded-r-lg">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <h3 className="font-medium text-gray-900">{event.title}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEventTypeColor(event.type)}`}>
                          {event.type === 'watering' && 'Tưới nước'}
                          {event.type === 'fertilizing' && 'Bón phân'}
                          {event.type === 'pruning' && 'Cắt tỉa'}
                          {event.type === 'repotting' && 'Thay chậu'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-1">{event.plant}</p>
                      <div className="flex items-center text-sm text-gray-500">
                        <Clock className="w-4 h-4 mr-1" />
                        {formatDate(event.date)}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                        Hoàn thành
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
