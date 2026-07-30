import { ImageOff } from 'lucide-react';
import { Button } from './Button';

export const EmptyState = ({
  icon: Icon = ImageOff,
  title = 'No Image Loaded',
  description = 'Upload an image or select a pre-set garment to get started.',
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30">
      <div className="w-14 h-14 bg-slate-800/60 rounded-2xl flex items-center justify-center text-slate-400 mb-4">
        <Icon size={28} />
      </div>
      <h4 className="text-base font-semibold text-white mb-1">{title}</h4>
      <p className="text-xs text-slate-400 max-w-sm mb-5">{description}</p>
      {actionLabel && onAction && (
        <Button variant="outline" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
