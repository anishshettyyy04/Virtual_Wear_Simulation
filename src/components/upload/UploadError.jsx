import { AlertTriangle, X, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';

/**
 * Reusable UploadError component for rendering user-friendly validation error messages.
 */
export const UploadError = ({
  error = 'An unexpected upload error occurred.',
  onDismiss,
  onRetry,
  className = '',
}) => {
  return (
    <div
      role="alert"
      className={`bg-rose-950/40 border border-rose-500/40 rounded-2xl p-4 sm:p-5 text-rose-200 shadow-lg shadow-rose-950/20 backdrop-blur-sm animate-fadeIn ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center flex-shrink-0 mt-0.5 border border-rose-500/30">
            <AlertTriangle size={20} />
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-rose-300">Upload Validation Error</h4>
            <p className="text-xs text-rose-200/90 leading-relaxed">{error}</p>
          </div>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-rose-400 hover:text-rose-200 transition-colors p-1 rounded-lg hover:bg-rose-500/20 focus:outline-none focus:ring-2 focus:ring-rose-500"
            aria-label="Dismiss error notification"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {(onRetry || onDismiss) && (
        <div className="flex items-center gap-2 mt-4 pt-3 border-t border-rose-500/20">
          {onRetry && (
            <Button
              variant="danger"
              size="sm"
              leftIcon={<RefreshCw size={13} />}
              onClick={onRetry}
            >
              Try Again
            </Button>
          )}
          {onDismiss && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              className="text-rose-300 hover:text-white hover:bg-rose-500/20"
            >
              Dismiss
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
