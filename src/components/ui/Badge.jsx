export const Badge = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  className = '',
}) => {
  const variants = {
    primary: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    secondary: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    danger: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    neutral: 'bg-slate-800/80 text-slate-300 border-slate-700/60',
  };

  const sizes = {
    sm: 'text-[10px] px-2 py-0.5 gap-1 font-medium',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {icon}
      <span>{children}</span>
    </span>
  );
};
