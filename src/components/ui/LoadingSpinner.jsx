import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 'md', label = 'Loading...', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-3 p-4 ${className}`}>
      <div className="relative">
        <div className={`${sizes[size]} rounded-full border-2 border-blue-500/20 animate-ping absolute inset-0`} />
        <Loader2 className={`${sizes[size]} text-blue-500 animate-spin`} />
      </div>
      {label && <p className="text-xs font-medium text-slate-400 animate-pulse">{label}</p>}
    </div>
  );
};
