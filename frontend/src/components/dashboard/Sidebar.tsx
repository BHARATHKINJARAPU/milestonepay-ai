import React from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderKanban, 
  FolderPlus, 
  LogOut, 
  Layers, 
  User as UserIcon,
  Home
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navItems = [
    { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
    { name: 'Projects', to: '/projects', icon: FolderKanban },
    { name: 'Create Project', to: '/projects/new', icon: FolderPlus },
  ];

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col justify-between h-full">
      {/* Brand & Navigation */}
      <div>
        {/* Brand header */}
        <div className="h-20 px-6 flex items-center border-b border-slate-800/80">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-violet-600 p-0.5 shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-slate-950 rounded-[9px] flex items-center justify-center">
                <Layers className="w-4 h-4 text-blue-400" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
                MilestonePay <span className="text-[10px] font-semibold px-1 py-0.2 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">AI</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono tracking-wider uppercase">Workspace</span>
            </div>
          </Link>
        </div>

        {/* Links */}
        <div className="px-4 py-6 space-y-1.5">
          <span className="px-3 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
            Menu
          </span>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/dashboard'}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-600/10'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900/80 border border-transparent'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}

          <div className="pt-4 border-t border-slate-900 mt-4 space-y-1">
            <Link
              to="/"
              onClick={onCloseMobile}
              className="flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-medium text-slate-500 hover:text-slate-300 hover:bg-slate-900/60 transition-colors"
            >
              <Home className="w-4 h-4" />
              <span>Landing Page</span>
            </Link>
          </div>
        </div>
      </div>

      {/* User profile & Logout */}
      <div className="p-4 border-t border-slate-800/80 space-y-3">
        {user && (
          <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-blue-400 shrink-0">
              <UserIcon className="w-4 h-4" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-white truncate">{user.full_name}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span className="text-[10px] font-mono text-slate-400 uppercase capitalize truncate">
                  {user.account_type}
                </span>
              </div>
            </div>
          </div>
        )}

        <button
          type="button"
          onClick={handleLogout}
          className="w-full py-2.5 px-3.5 rounded-xl text-xs font-medium text-rose-400 hover:text-rose-300 hover:bg-rose-950/30 border border-transparent hover:border-rose-900/40 transition-all flex items-center justify-center gap-2"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
