import { Download, Share2, RefreshCw, Upload } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export const ActionToolbar = ({
  onDownload,
  onShare,
  onRetry,
  onNewUpload,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
      <div className="flex items-center gap-2">
        <Button variant="gradient" size="md" leftIcon={<Download size={18} />} onClick={onDownload}>
          Download HD Render
        </Button>
        <Button variant="secondary" size="md" leftIcon={<Share2 size={18} />} onClick={onShare}>
          Share Result
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="outline" size="md" leftIcon={<RefreshCw size={16} />} onClick={onRetry}>
          Re-Simulate
        </Button>
        <Button variant="ghost" size="md" leftIcon={<Upload size={16} />} onClick={onNewUpload}>
          New Upload
        </Button>
      </div>
    </div>
  );
};
