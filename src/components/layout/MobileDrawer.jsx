import { useEffect, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { X, Shirt, ArrowRight, Cpu, LogOut, UserCheck, LogIn } from 'lucide-react';
import { APP_CONFIG } from '@/constants/appConfig';
import { useAuth } from '@/hooks/useAuth';
import { useSimulation } from '@/hooks/useSimulation';

/**
 * Mobile Navigation Drawer component with complete accessibility features:
 * - Focus trap inside drawer while active
 * - Focus moves inside on open and returns to menu button on close
 * - ESC key closes drawer
 * - Backdrop click closes drawer
 * - Semantic ARIA attributes (role="dialog", aria-modal="true")
 */
export const MobileDrawer = ({ isOpen, onClose, triggerRef }) => {
  const drawerRef = useRef(null);
  const closeButtonRef = useRef(null);
  const previousActiveElementRef = useRef(null);
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, login } = useAuth();
  const { resetSimulation } = useSimulation();

  useEffect(() => {
    if (isOpen) {
      // Save previously focused element (e.g. menu button) for focus restoration
      previousActiveElementRef.current = triggerRef?.current || document.activeElement;
      document.body.style.overflow = 'hidden';

      // Automatically move focus into drawer close button after render
      const focusTimer = setTimeout(() => {
        if (closeButtonRef.current) {
          closeButtonRef.current.focus();
        }
      }, 50);

      // Handle ESC key press & Focus Trapping inside drawer
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          e.preventDefault();
          onClose();
          return;
        }

        if (e.key === 'Tab' && drawerRef.current) {
          const focusableElements = drawerRef.current.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
          );

          if (focusableElements.length === 0) return;

          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];

          if (e.shiftKey) {
            // Shift + Tab: wrap to last element if currently at first
            if (document.activeElement === firstElement) {
              e.preventDefault();
              lastElement.focus();
            }
          } else {
            // Tab: wrap to first element if currently at last
            if (document.activeElement === lastElement) {
              e.preventDefault();
              firstElement.focus();
            }
          }
        }
      };

      window.addEventListener('keydown', handleKeyDown);

      return () => {
        clearTimeout(focusTimer);
        window.removeEventListener('keydown', handleKeyDown);
        document.body.style.overflow = 'unset';

        // Return focus to menu trigger button after closing drawer
        if (previousActiveElementRef.current && typeof previousActiveElementRef.current.focus === 'function') {
          previousActiveElementRef.current.focus();
        }
      };
    }
  }, [isOpen, onClose, triggerRef]);

  const handleLogout = async () => {
    onClose();
    await logout();
    resetSimulation();
    navigate('/');
  };

  const handleQuickLogin = async () => {
    onClose();
    await login({ email: 'demo@virtualwear.ai' });
  };

  if (!isOpen) return null;

  const navLinks = [
    { label: 'Home Page', path: '/', desc: 'App overview & features' },
    { label: 'Upload Avatar & Garment', path: '/upload', desc: 'Prepare your try-on simulation' },
    { label: 'Simulation Result', path: '/result', desc: 'Inspect AI render & fit analytics' },
  ];

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Mobile Navigation Menu"
      id="mobile-navigation-drawer"
      className="fixed inset-0 z-50 md:hidden"
    >
      {/* Backdrop overlay - clicking closes drawer */}
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-out Panel */}
      <div
        ref={drawerRef}
        className="fixed right-0 top-0 bottom-0 w-4/5 max-w-sm bg-slate-950 border-l border-slate-800 p-6 flex flex-col justify-between shadow-2xl z-10 animate-in slide-in-from-right duration-200"
      >
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
              ref={closeButtonRef}
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 rounded-xl border border-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Close Mobile Navigation Menu"
            >
              <X size={18} />
            </button>
          </div>

          {/* User Account / Auth Section */}
          <div className="mb-6 p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
            {isAuthenticated ? (
              <>
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
                    <UserCheck size={16} />
                  </div>
                  <div>
                    <span className="block text-xs font-semibold text-white truncate max-w-[140px]">
                      {user?.name || 'User'}
                    </span>
                    <span className="text-[10px] text-slate-400">Authenticated</span>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  aria-label="Log Out"
                  title="Log Out"
                >
                  <LogOut size={16} />
                </button>
              </>
            ) : (
              <div className="w-full flex items-center justify-between">
                <span className="text-xs text-slate-400">Guest User</span>
                <button
                  onClick={handleQuickLogin}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors"
                >
                  <LogIn size={14} />
                  <span>Log In</span>
                </button>
              </div>
            )}
          </div>

          {/* Navigation Items */}
          <nav className="flex flex-col gap-2" aria-label="Mobile menu navigation">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `p-3.5 rounded-xl border flex items-center justify-between transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 ${
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
          </nav>
        </div>

        {/* Footer Info */}
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

export default MobileDrawer;
