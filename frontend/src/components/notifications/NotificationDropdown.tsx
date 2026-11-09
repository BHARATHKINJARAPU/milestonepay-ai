import React from 'react';
import { Link } from 'react-router-dom';
import { CheckCheck, ExternalLink, Loader2 } from 'lucide-react';
import { Notification } from '../../types/notification';
import { NotificationItem } from './NotificationItem';

interface NotificationDropdownProps {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  onMarkRead: (id: string) => void;
  onMarkAllRead: () => void;
  onClose: () => void;
}

export const NotificationDropdown: React.FC<NotificationDropdownProps> = ({
  notifications,
  unreadCount,
  isLoading,
  onMarkRead,
  onMarkAllRead,
  onClose,
}) => {
  return (
    <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl border border-slate-800 bg-slate-950/95 backdrop-blur-xl p-3 shadow-2xl shadow-black/80 z-50">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 px-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-white">Notifications</span>
          {unreadCount > 0 && (
            <span className="px-1.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 text-[10px] font-mono font-bold border border-cyan-500/30">
              {unreadCount} new
            </span>
          )}
        </div>

        {unreadCount > 0 && (
          <button
            type="button"
            onClick={onMarkAllRead}
            className="flex items-center gap-1 text-[11px] font-semibold text-slate-400 hover:text-cyan-400 transition-colors cursor-pointer"
          >
            <CheckCheck className="h-3.5 w-3.5" />
            <span>Mark all read</span>
          </button>
        )}
      </div>

      {/* Notifications List */}
      <div className="max-h-80 overflow-y-auto space-y-1.5 py-2">
        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-slate-500">
            <Loader2 className="h-5 w-5 animate-spin" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="py-8 text-center text-slate-500 text-xs">
            No notifications yet.
          </div>
        ) : (
          notifications.slice(0, 6).map((n) => (
            <NotificationItem
              key={n.id}
              notification={n}
              onMarkRead={onMarkRead}
              onCloseDropdown={onClose}
            />
          ))
        )}
      </div>

      {/* Footer Link to Full Page */}
      <div className="pt-2 border-t border-slate-800 text-center">
        <Link
          to="/notifications"
          onClick={onClose}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-400 hover:text-cyan-300 py-1 transition-colors"
        >
          <span>View all notifications</span>
          <ExternalLink className="h-3 w-3" />
        </Link>
      </div>
    </div>
  );
};

