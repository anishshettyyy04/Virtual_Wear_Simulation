import { useRef } from 'react';
import { RefreshCw, Trash2, CheckCircle2, FileImage, Maximize2, Calendar, HardDrive } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

/**
 * Reusable Image Preview component displaying uploaded image, details, resolution,
 * timestamp, replace button, and remove button.
 */
export const ImagePreview = ({
  previewURL,
  fileName,
  fileSize,
  imageWidth,
  imageHeight,
  uploadTimestamp,
  onReplace,
  onRemove,
  className = '',
}) => {
  const replaceInputRef = useRef(null);

  const handleReplaceClick = () => {
    if (replaceInputRef.current) {
      replaceInputRef.current.click();
    }
  };

  const handleReplaceFileChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0 && onReplace) {
      onReplace(files[0]);
    }
  };

  return (
    <div className={`bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-5 shadow-xl transition-all duration-300 ${className}`}>
      {/* Hidden File Input for Replace Action */}
      <input
        ref={replaceInputRef}
        type="file"
        accept="image/png, image/jpeg, image/jpg, image/webp"
        onChange={handleReplaceFileChange}
        className="hidden"
        aria-hidden="true"
      />

      {/* Header Badge & Title */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckCircle2 size={18} className="text-emerald-400" />
          <h4 className="text-sm font-bold text-white">Image Preview Ready</h4>
        </div>
        <Badge variant="success" size="sm">
          Validated
        </Badge>
      </div>

      {/* Main Preview Aspect Container */}
      <div className="relative group rounded-xl overflow-hidden bg-slate-900 border border-slate-800/80 aspect-square sm:aspect-[4/3] max-h-80 flex items-center justify-center">
        {previewURL ? (
          <img
            src={previewURL}
            alt={fileName || 'Uploaded image preview'}
            className="w-full h-full object-contain p-2 transition-transform duration-300 group-hover:scale-[1.02]"
          />
        ) : (
          <div className="text-slate-500 text-xs flex flex-col items-center gap-2">
            <FileImage size={32} />
            <span>No preview available</span>
          </div>
        )}
      </div>

      {/* Image Metadata Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div className="space-y-1">
          <span className="text-slate-400 text-[11px] flex items-center gap-1 font-medium">
            <FileImage size={12} className="text-blue-400" /> File Name
          </span>
          <p className="font-semibold text-slate-200 truncate font-mono" title={fileName}>
            {fileName || 'Untitled.jpg'}
          </p>
        </div>

        <div className="space-y-1">
          <span className="text-slate-400 text-[11px] flex items-center gap-1 font-medium">
            <HardDrive size={12} className="text-purple-400" /> File Size
          </span>
          <p className="font-semibold text-slate-200 font-mono">
            {fileSize || 'N/A'}
          </p>
        </div>

        <div className="space-y-1">
          <span className="text-slate-400 text-[11px] flex items-center gap-1 font-medium">
            <Maximize2 size={12} className="text-emerald-400" /> Resolution
          </span>
          <p className="font-semibold text-slate-200 font-mono">
            {imageWidth && imageHeight ? `${imageWidth} × ${imageHeight} px` : 'Calculating...'}
          </p>
        </div>

        <div className="space-y-1">
          <span className="text-slate-400 text-[11px] flex items-center gap-1 font-medium">
            <Calendar size={12} className="text-amber-400" /> Upload Time
          </span>
          <p className="font-semibold text-slate-200 font-mono">
            {uploadTimestamp || 'Just now'}
          </p>
        </div>
      </div>

      {/* Action Buttons: Replace & Remove */}
      <div className="flex items-center gap-3 pt-1">
        <Button
          variant="secondary"
          size="md"
          leftIcon={<RefreshCw size={15} />}
          onClick={handleReplaceClick}
          className="flex-1"
        >
          Replace Image
        </Button>
        <Button
          variant="danger"
          size="md"
          leftIcon={<Trash2 size={15} />}
          onClick={onRemove}
          className="flex-1"
        >
          Remove Image
        </Button>
      </div>
    </div>
  );
};
