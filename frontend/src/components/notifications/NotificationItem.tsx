import React from 'react';
import { Link } from 'react-router-dom';
import {
  Bell,
  CheckCircle2,
  Clock,
  CreditCard,
  FileText,
  FolderKanban,
  Sparkles,
  Trash2,
} from 'lucide-react';
import { Notification } from '../../types/notification';

interface NotificationItemProps {
  notification: Notification;
  onMarkRead?: (id: string) => void;
  onDelete?: (id: string) => void;
  onCloseDropdown?: () => void;
}

export const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onMarkRead,
  onDelete,
  onCloseDropdown,
}) => {
  const getIcon = () => {
    switch (notification.notification_type) {
      case 'payment_captured':
        return <CreditCard className="h-4 w-4 text-emerald-400" />;
      case 'milestone_approved':
      case 'client_approved':
        return <CheckCircle2 className="h-4 w-4 text-cyan-400" />;
      case 'submission_received':
        return <FileText className="h-4 w-4 text-blue-400" />;
      case 'collaborator_added':
      case 'project_created':
        return <FolderKanban className="h-4 w-4 text-violet-400" />;
      case 'ai_evaluation_completed':
        return <Sparkles className="h-4 w-4 text-amber-400" />;
      default:
        return <Bell className="h-4 w-4 text-slate-400" />;
    }
  };

  const formattedTime = new Date(notification.created_at).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  const content = (
    <div
      className={`group relative flex items-start gap-3 p-3.5 rounded-xl transition-all ${
        notification.is_read
          ? 'bg-slate-900/40 hover:bg-slate-800/40 opacity-75 hover:opacity-100'
          : 'bg-blue-950/20 hover:bg-blue-950/30 border-l-2 border-cyan-500'
      }`}
    >
      <div className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-slate-800/80 border border-slate-700/60">
        {getIcon()}
      </div>

      <div className="flex-1 min-w-0 pr-6">
        <div className="flex items-center gap-2">
          <p className="text-xs font-semibold text-white truncate">{notification.title}</p>
          {!notification.is_read && (
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 flex-shrink-0 animate-pulse" />
          )}
        </div>
        <p className="mt-0.5 text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
          {notification.message}
        </p>
        <div className="mt-1 flex items-center gap-1.5 text-[10px] text-slate-500 font-mono">
          <Clock className="h-3 w-3" />
          <span>{formattedTime}</span>
        </div>
      </div>

      <div className="absolute right-2 top-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {!notification.is_read && onMarkRead && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onMarkRead(notification.id);
            }}
            title="Mark as read"
            className="p-1 rounded text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
          </button>
        )}
        {onDelete && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onDelete(notification.id);
            }}
            title="Delete notification"
            className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    </div>
  );

  if (notification.action_url) {
    return (
      <Link
        to={notification.action_url}
        onClick={() => {
          if (!notification.is_read && onMarkRead) {
            onMarkRead(notification.id);
          }
          if (onCloseDropdown) {
            onCloseDropdown();
          }
        }}
        className="block"
      >
        {content}
      </Link>
    );
  }

  return content;
};

