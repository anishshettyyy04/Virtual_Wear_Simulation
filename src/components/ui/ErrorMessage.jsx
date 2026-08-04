import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export const ErrorMessage = ({
  title = 'An error occurred',
  message,
  onRetry,
  className = '',
}) => {
  if (!message) return null;

  return (
    <div
      className={`rounded-2xl bg-rose-500/10 border border-rose-500/20 p-4 flex items-start gap-3 text-rose-300 ${className}`}
      role="alert"
    >
      <AlertCircle size={20} className="shrink-0 text-rose-400 mt-0.5" />
      <div className="flex-1 text-xs">
        <strong className="block text-sm font-semibold text-rose-200 mb-0.5">{title}</strong>
        <span>{typeof message === 'object' ? (message?.message || JSON.stringify(message)) : String(message)}</span>
      </div>
      {onRetry && (
        <Button variant="ghost" size="sm" onClick={onRetry} className="shrink-0 text-rose-300 hover:text-white">
          <RefreshCw size={14} className="mr-1" /> Retry
        </Button>
      )}
    </div>
  );
};
