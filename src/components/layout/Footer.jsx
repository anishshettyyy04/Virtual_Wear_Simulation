import { Shirt, Github, Twitter, Layers, Code2, Users } from 'lucide-react';
import { APP_CONFIG } from '@/constants/appConfig';

export const Footer = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-800/80 pt-12 pb-8 text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-12 border-b border-slate-900">
          {/* Column 1: Project Overview */}
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <Shirt size={18} />
              </div>
              <span className="font-bold text-white text-lg font-display">
                {APP_CONFIG.NAME}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              High-precision AI Virtual Wear Simulation platform rendering fabric drape, posture alignment, and real-time apparel fitting.
            </p>
            <div className="flex items-center gap-3 pt-2 text-slate-400">
              <a
                href="#github"
                className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center hover:text-white hover:border-slate-700 transition-colors"
                aria-label="GitHub Repository"
              >
                <Github size={16} />
              </a>
              <a
                href="#twitter"
                className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center hover:text-white hover:border-slate-700 transition-colors"
                aria-label="Twitter Profile"
              >
                <Twitter size={16} />
              </a>
            </div>
          </div>

          {/* Column 2: Quick Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Layers size={14} className="text-indigo-400" /> Quick Navigation
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="/" className="hover:text-indigo-400 transition-colors">Home Landing Page</a>
              </li>
              <li>
                <a href="/upload" className="hover:text-indigo-400 transition-colors">Upload Avatar & Garment</a>
              </li>
              <li>
                <a href="/result" className="hover:text-indigo-400 transition-colors">Simulation Result & Analytics</a>
              </li>
            </ul>
          </div>

          {/* Column 3: Tech Stack */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Code2 size={14} className="text-purple-400" /> Technology Foundation
            </h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center justify-between">
                <span>Frontend Engine:</span>
                <span className="text-slate-300 font-mono">React 19 + Vite</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Styling & Design:</span>
                <span className="text-slate-300 font-mono">Tailwind CSS v4</span>
              </li>
              <li className="flex items-center justify-between">
                <span>API Protocol:</span>
                <span className="text-slate-300 font-mono">Axios Client</span>
              </li>
            </ul>
          </div>

          {/* Column 4: Team Members Placeholder */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Users size={14} className="text-pink-400" /> Team Members Placeholder
            </h4>
            <ul className="space-y-2 text-xs">
              {APP_CONFIG.TEAM_MEMBERS.map((member, idx) => (
                <li key={idx} className="flex flex-col bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
                  <span className="text-slate-200 font-medium">{member.name}</span>
                  <span className="text-[10px] text-slate-500">{member.role}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} {APP_CONFIG.NAME}. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span className="inline-block w-2 h-2 rounded-full bg-indigo-500"></span>
            <span>Production Ready Frontend Architecture</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
