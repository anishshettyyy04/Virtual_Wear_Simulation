import { Loader2 } from 'lucide-react';

export const LoadingFallback = ({ message = 'Loading module...' }) => {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center p-8">
      <div className="relative flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border-2 border-indigo-500/20 animate-ping absolute" />
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
      </div>
      <p className="mt-4 text-slate-400 text-sm font-medium animate-pulse">{message}</p>
    </div>
  );
};
