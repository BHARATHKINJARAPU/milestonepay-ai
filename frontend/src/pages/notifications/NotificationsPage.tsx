import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Bell,
  CheckCheck,
  Filter,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { NotificationItem } from '../../components/notifications/NotificationItem';
import {
  deleteNotification,
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '../../lib/api';
import { Notification } from '../../types/notification';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const NotificationsPage: React.FC = () => {
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadNotifications = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getNotifications({ unread_only: unreadOnly, limit: 50 });
      if (data) {
        setNotifications(data.notifications);
        setUnreadCount(data.unread_count);
        setTotal(data.total);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to load notifications.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [unreadOnly]);

  const handleMarkRead = async (id: string) => {
    try {
      await markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {
      // Failed
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch {
      // Failed
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      setTotal((t) => Math.max(0, t - 1));
    } catch {
      // Failed
    }
  };

  return (
    <div className="space-y-8 pb-16">
      <DashboardHeader
        title="Notifications"
        subtitle="Stay updated on milestone agreements, deliverable reviews, and payment settlements."
        onOpenMobileMenu={onOpenMobileMenu}
      />

      {/* Action Controls & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400 ml-1" />
          <span className="text-xs font-semibold text-slate-400">Filter:</span>
          <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800">
            <button
              type="button"
              onClick={() => setUnreadOnly(false)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors cursor-pointer ${
                !unreadOnly
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              All ({total})
            </button>
            <button
              type="button"
              onClick={() => setUnreadOnly(true)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors cursor-pointer ${
                unreadOnly
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Unread ({unreadCount})
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <button
              type="button"
              onClick={handleMarkAllRead}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-200 hover:bg-slate-700 hover:text-white transition-colors cursor-pointer"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              <span>Mark all as read</span>
            </button>
          )}

          <button
            type="button"
            onClick={loadNotifications}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition-colors cursor-pointer"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Notifications List */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-500 space-y-3">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
          <p className="text-xs font-mono">Loading notifications...</p>
        </div>
      ) : errorMessage ? (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-6 text-center text-xs text-rose-300">
          {errorMessage}
        </div>
      ) : notifications.length === 0 ? (
        <div className="rounded-3xl border border-slate-800/80 bg-slate-900/40 py-16 text-center space-y-3">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-800/60 border border-slate-700/60 text-slate-400">
            <Bell className="h-6 w-6" />
          </div>
          <p className="text-sm font-semibold text-white">No notifications found</p>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            {unreadOnly
              ? 'You have caught up with all notifications. Switch to "All" to view previous activity.'
              : 'When actions occur across your projects or milestones, real-time alerts will appear here.'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <NotificationItem
              key={n.id}
              notification={n}
              onMarkRead={handleMarkRead}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
};

