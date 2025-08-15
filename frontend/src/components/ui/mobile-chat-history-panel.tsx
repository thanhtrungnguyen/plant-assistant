/**
 * Mobile chat history panel component
 */

"use client";

import { Button } from "@/components/ui/button";
import { type Conversation } from "@/lib/chat-api";
import { formatDate, truncateMessage } from "@/lib/chat-utils";
import { Clock, MessageCircle, Plus, Trash2, X } from "lucide-react";

interface MobileChatHistoryPanelProps {
  isOpen: boolean;
  conversations: Conversation[];
  currentConversationId?: string;
  isLoading: boolean;
  onClose: () => void;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
}

export function MobileChatHistoryPanel({
  isOpen,
  conversations,
  currentConversationId,
  isLoading,
  onClose,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}: MobileChatHistoryPanelProps) {
  if (!isOpen) return null;

  const handleSelectConversation = (conversationId: string) => {
    onSelectConversation(conversationId);
    onClose();
  };

  const handleNewConversation = () => {
    onNewConversation();
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed inset-y-0 right-0 w-80 max-w-[90vw] bg-white shadow-lg z-50 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-gray-900">Cuộc trò chuyện</h2>
            <button
              onClick={onClose}
              className="p-1 rounded-md hover:bg-gray-100 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <Button
            size="sm"
            onClick={handleNewConversation}
            className="w-full mb-2"
          >
            <Plus className="h-4 w-4 mr-2" />
            Cuộc trò chuyện mới
          </Button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="text-center text-gray-500 py-8">
              <p className="text-sm">Đang tải...</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <MessageCircle className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">Chưa có cuộc trò chuyện nào</p>
              <p className="text-xs mt-1">Bắt đầu chat để tạo lịch sử</p>
            </div>
          ) : (
            <div className="space-y-3">
              {conversations.map((conversation) => (
                <div
                  key={conversation.conversation_id}
                  className={`group relative rounded-lg border p-3 cursor-pointer transition-colors hover:bg-gray-50 ${
                    currentConversationId === conversation.conversation_id
                      ? "bg-blue-50 border-blue-200"
                      : "border-gray-200"
                  }`}
                  onClick={() => handleSelectConversation(conversation.conversation_id)}
                >
                  {/* Conversation Content */}
                  <div className="pr-8">
                    {/* Last Message */}
                    {conversation.last_message && (
                      <p className="text-sm font-medium text-gray-900 mb-1">
                        {truncateMessage(conversation.last_message)}
                      </p>
                    )}

                    {/* Metadata */}
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      <span>{formatDate(conversation.last_message_time)}</span>
                      {conversation.plant_id && (
                        <>
                          <span>•</span>
                          <span>Cây #{conversation.plant_id}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Delete Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conversation.conversation_id);
                    }}
                    className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            {conversations.length} cuộc trò chuyện
          </p>
        </div>
      </div>
    </>
  );
}
