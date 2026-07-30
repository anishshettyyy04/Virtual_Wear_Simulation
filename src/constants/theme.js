export const THEME = {
  colors: {
    primary: '#6366f1',
    primaryHover: '#4f46e5',
    secondary: '#8b5cf6',
    accent: '#ec4899',
    background: '#030712',
    surface: '#111827',
    surfaceLight: '#1f2937',
    textPrimary: '#f9fafb',
    textSecondary: '#9ca3af',
    border: 'rgba(255, 255, 255, 0.08)',
  },
  statusBadges: {
    ready: { label: 'Model Ready', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
    processing: { label: 'Simulating', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
    completed: { label: 'High Confidence', color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' },
    error: { label: 'Failed', color: 'bg-rose-500/10 text-rose-400 border-rose-500/20' },
  },
};
