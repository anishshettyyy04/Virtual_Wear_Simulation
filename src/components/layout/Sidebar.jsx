import { NavLink } from 'react-router-dom';
import { Home, Upload, BarChart2, Cpu, Sparkles, Layers, ArrowUpRight } from 'lucide-react';
import { APP_CONFIG } from '@/constants/appConfig';

export const Sidebar = () => {
  const navItems = [
    { label: 'Home', path: '/', icon: Home, badge: 'Main' },
    { label: 'Upload', path: '/upload', icon: Upload, badge: 'Studio' },
    { label: 'Results', path: '/result', icon: BarChart2, badge: 'Analytics' },
  ];

  return (
    <aside className="hidden md:flex flex-col w-64 shrink-0 border-r border-slate-800/80 bg-slate-950/60 p-4 space-y-6 min-h-[calc(100vh-4rem)] sticky top-16 self-start">
      {/* Sidebar Header Section */}
      <div className="px-3 py-2 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl border border-blue-500/20">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles size={14} className="text-blue-400" />
          <span className="text-xs font-extrabold text-white tracking-wider uppercase">
            Virtual Wear Engine
          </span>
        </div>
        <p className="text-[11px] text-slate-400">
          AI Try-On Simulation Studio
        </p>
      </div>

      {/* Main Navigation Links */}
      <div className="space-y-1">
        <span className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
          Navigation
        </span>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25 border border-blue-400/30'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent'
                  }`
                }
              >
                <div className="flex items-center gap-2.5">
                  <Icon size={18} />
                  <span>{item.label}</span>
                </div>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/60">
                  {item.badge}
                </span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* AI Processing Mode Widget */}
      <div className="glass-card p-3.5 rounded-xl space-y-2 border border-slate-800">
        <div className="flex items-center justify-between text-xs font-bold text-slate-200">
          <span className="flex items-center gap-1.5">
            <Cpu size={14} className="text-purple-400" /> Pipeline Status
          </span>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
        <div className="text-[11px] text-slate-400 space-y-1">
          <div className="flex justify-between">
            <span>Model:</span>
            <span className="text-slate-200 font-mono">v0.1 Ready</span>
          </div>
          <div className="flex justify-between">
            <span>Mode:</span>
            <span className="text-blue-400 font-mono">Frontend Only</span>
          </div>
        </div>
      </div>

      {/* Quick Launch CTA Card */}
      <div className="mt-auto pt-4 border-t border-slate-800/80 space-y-3">
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-xs">
          <div className="flex items-center justify-between text-slate-300 font-semibold mb-1">
            <span>Quick Start</span>
            <ArrowUpRight size={14} className="text-blue-400" />
          </div>
          <p className="text-[11px] text-slate-400 mb-2">
            Try our sample avatar and garment configuration.
          </p>
          <NavLink
            to="/upload"
            className="block text-center w-full py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 font-medium text-[11px] border border-blue-500/30 transition-colors"
          >
            Open Studio
          </NavLink>
        </div>

        {/* Footer Version Tag */}
        <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono px-1">
          <span className="flex items-center gap-1">
            <Layers size={10} /> {APP_CONFIG.NAME}
          </span>
          <span>v0.1</span>
        </div>
      </div>
    </aside>
  );
};
