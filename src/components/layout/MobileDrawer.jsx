import { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { X, Shirt, ArrowRight, Cpu } from 'lucide-react';
import { APP_CONFIG } from '@/constants/appConfig';

export const MobileDrawer = ({ isOpen, onClose }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const navLinks = [
    { label: 'Home Page', path: '/', desc: 'App overview & features' },
    { label: 'Upload Avatar & Garment', path: '/upload', desc: 'Prepare your try-on simulation' },
    { label: 'Simulation Result', path: '/result', desc: 'Inspect AI render & fit analytics' },
  ];

  return (
    <div className="fixed inset-0 z-50 md:hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Slide-out Panel */}
      <div className="fixed right-0 top-0 bottom-0 w-4/5 max-w-sm bg-slate-950 border-l border-slate-800 p-6 flex flex-col justify-between shadow-2xl z-10 animate-in slide-in-from-right duration-200">
        <div>
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <Shirt size={18} />
              </div>
              <span className="font-bold text-white text-base font-display">
                {APP_CONFIG.NAME}
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white bg-slate-900 rounded-lg border border-slate-800"
              aria-label="Close Mobile Drawer"
            >
              <X size={18} />
            </button>
          </div>

          {/* Navigation Items */}
          <div className="flex flex-col gap-2">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `p-3.5 rounded-xl border flex items-center justify-between transition-all ${
                    isActive
                      ? 'bg-indigo-600/10 border-indigo-500/40 text-indigo-400'
                      : 'bg-slate-900/40 border-slate-800/60 text-slate-300 hover:bg-slate-900'
                  }`
                }
              >
                <div>
                  <span className="block font-semibold text-sm">{link.label}</span>
                  <span className="text-[11px] text-slate-500">{link.desc}</span>
                </div>
                <ArrowRight size={16} className="opacity-60" />
              </NavLink>
            ))}
          </div>
        </div>

        {/* Footer info */}
        <div className="pt-6 border-t border-slate-800">
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-xs">
            <Cpu size={14} className="text-emerald-400" />
            <span>AI GPU Backend: Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};
