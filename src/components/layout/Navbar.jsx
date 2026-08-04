import { useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Shirt, Menu, Sparkles, Cpu, Github, LogOut, UserCheck, LogIn } from 'lucide-react';
import { APP_CONFIG } from '@/constants/appConfig';
import { useAuth } from '@/hooks/useAuth';
import { useSimulation } from '@/hooks/useSimulation';

export const Navbar = ({ onOpenMobileMenu, isMobileMenuOpen = false }) => {
  const menuButtonRef = useRef(null);
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, login } = useAuth();
  const { resetSimulation, modelStatus } = useSimulation();

  const handleOpenMenu = () => {
    if (onOpenMobileMenu) {
      onOpenMobileMenu(menuButtonRef);
    }
  };

  const handleLogout = async () => {
    await logout();
    resetSimulation();
    navigate('/');
  };

  const handleQuickLogin = async () => {
    await login({ email: 'demo@virtualwear.ai' });
  };

  const navLinks = [
    { label: 'Home', path: '/' },
    { label: 'Upload', path: '/upload' },
    { label: 'Results', path: '/result' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <NavLink
            to="/"
            className="flex items-center gap-2.5 group focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-xl p-1"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 p-0.5 shadow-lg shadow-blue-600/30 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Shirt
                  size={20}
                  className="text-blue-400 group-hover:text-purple-400 transition-colors"
                />
              </div>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg text-white tracking-tight font-display">
                  {APP_CONFIG.NAME}
                </span>
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  <Sparkles size={10} /> v0.1
                </span>
              </div>
              <span className="text-[10px] text-slate-400 -mt-1 hidden sm:block">
                AI Virtual Try-On Engine
              </span>
            </div>
          </NavLink>

          {/* Desktop Navigation Links */}
          <nav
            className="hidden md:flex items-center gap-1 bg-slate-900/80 p-1.5 rounded-full border border-slate-800/80"
            aria-label="Desktop navigation"
          >
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) =>
                  `px-5 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          {/* AI Status & Auth Controls */}
          <div className="hidden sm:flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium ${modelStatus?.isReady ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'}`}>
              <span className="relative flex h-2 w-2">
                {modelStatus?.isReady && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                <span className={`relative inline-flex rounded-full h-2 w-2 ${modelStatus?.isReady ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
              </span>
              <Cpu size={14} />
              <span className="hidden lg:inline">{modelStatus?.isReady ? 'Engine Online' : 'Engine Offline'}</span>
            </div>

            {/* Auth State Button / User Badge */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium">
                  <UserCheck size={14} className="text-blue-400" />
                  <span className="max-w-[100px] truncate">{user?.name || 'User'}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-slate-800 transition-colors flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-rose-500"
                  title="Sign Out"
                  aria-label="Sign Out"
                >
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <button
                onClick={handleQuickLogin}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <LogIn size={14} />
                <span>Log In</span>
              </button>
            )}

            {/* GitHub Repository Link */}
            <a
              href="https://github.com/anishshettyyy04/Virtual_Wear_Simulation"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/80 border border-slate-800 transition-colors flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="GitHub Repository"
              title="GitHub Repository"
            >
              <Github size={18} />
            </a>
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="flex md:hidden items-center gap-2">
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-slate-800 border border-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Sign Out"
                title="Sign Out"
              >
                <LogOut size={18} />
              </button>
            ) : (
              <button
                onClick={handleQuickLogin}
                className="px-2.5 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Log In
              </button>
            )}
            <button
              ref={menuButtonRef}
              onClick={handleOpenMenu}
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-navigation-drawer"
              className="p-2 text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 rounded-xl border border-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Open Mobile Navigation Menu"
            >
              <Menu size={20} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
