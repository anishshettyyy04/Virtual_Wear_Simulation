import { Loader2 } from 'lucide-react';

export const Loader = ({ size = 'md', text = 'Processing simulation...', fullScreen = false }) => {
  const sizeMap = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const content = (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className="relative">
        <div className={`${sizeMap[size]} rounded-full border-2 border-indigo-500/20 animate-ping absolute`} />
        <Loader2 className={`${sizeMap[size]} text-indigo-500 animate-spin`} />
      </div>
      {text && <p className="text-xs font-medium text-slate-400 animate-pulse">{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};
