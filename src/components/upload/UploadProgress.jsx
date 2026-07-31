import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

/**
 * Reusable UploadProgress component displaying fake upload progress bar, status text,
 * and LoadingSpinner.
 */
export const UploadProgress = ({
  progress = 0,
  fileName = 'file',
  statusLabel = 'Processing & Validating Image...',
  className = '',
}) => {
  return (
    <div className={`bg-slate-950 border border-slate-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center space-y-6 shadow-xl ${className}`}>
      {/* Loading Spinner */}
      <LoadingSpinner size="lg" label="" />

      {/* Status Heading & Subtext */}
      <div className="space-y-1 max-w-sm">
        <h4 className="text-sm font-bold text-white">{statusLabel}</h4>
        {fileName && (
          <p className="text-xs text-slate-400 font-mono truncate" title={fileName}>
            {fileName}
          </p>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full max-w-xs space-y-2">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Uploading to local memory</span>
          <span className="font-semibold text-blue-400">{progress}%</span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-600 rounded-full transition-all duration-150 ease-out"
            style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};
