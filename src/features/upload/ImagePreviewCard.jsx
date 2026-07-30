import { Trash2, CheckCircle2 } from 'lucide-react';
import { formatFileSize } from '@/utils/fileHelpers';
import { Badge } from '@/components/ui/Badge';

export const ImagePreviewCard = ({ title, imageData, onRemove }) => {
  if (!imageData) return null;

  return (
    <div className="relative glass-card rounded-2xl p-4 border border-slate-800 flex flex-col gap-3 group">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          {title}
        </span>
        <Badge variant="success" size="sm" icon={<CheckCircle2 size={12} />}>
          Ready
        </Badge>
      </div>

      {/* Image Preview Window */}
      <div className="relative w-full h-56 rounded-xl overflow-hidden bg-slate-950 border border-slate-800/80 flex items-center justify-center">
        <img
          src={imageData.previewUrl}
          alt={imageData.name || title}
          className="w-full h-full object-contain p-2"
        />
        {onRemove && (
          <button
            onClick={onRemove}
            className="absolute top-3 right-3 p-2 bg-rose-600/80 hover:bg-rose-600 text-white rounded-xl backdrop-blur-md opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
            title="Remove Image"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      {/* Image Meta details */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span className="truncate max-w-[180px] font-medium text-slate-300">
          {imageData.name || 'Custom Upload'}
        </span>
        {imageData.size && (
          <span className="font-mono text-[11px] text-slate-500">
            {formatFileSize(imageData.size)}
          </span>
        )}
      </div>
    </div>
  );
};
