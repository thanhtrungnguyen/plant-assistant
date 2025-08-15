/**
 * Shared utilities for chat history components
 */

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

  if (diffInHours < 1) {
    return "Vừa xong";
  } else if (diffInHours < 24) {
    return `${diffInHours} giờ trước`;
  } else if (diffInHours < 48) {
    return "Hôm qua";
  } else {
    const days = Math.floor(diffInHours / 24);
    return `${days} ngày trước`;
  }
}

export function truncateMessage(message: string, maxLength: number = 50): string {
  if (message.length <= maxLength) return message;
  return message.substring(0, maxLength) + "...";
}
