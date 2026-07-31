import { useRef } from 'react';
import { UploadCloud, Image as ImageIcon, FileText, HardDrive } from 'lucide-react';
import { Button } from '@/components/ui/Button';

/**
 * Reusable drag & drop upload dropzone component.
 * Supports keyboard accessibility, drag states, file type/size guidance.
 */
export const UploadDropzone = ({
  onFileSelect,
  onDragOver,
  onDragLeave,
  onDrop,
  uploadStatus = 'idle',
  isDisabled = false,
  className = '',
}) => {
  const fileInputRef = useRef(null);
  const isDragging = uploadStatus === 'dragging';

  const triggerFilePicker = () => {
    if (!isDisabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleKeyDown = (e) => {
    if (isDisabled) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      triggerFilePicker();
    }
  };

  return (
    <div
      tabIndex={isDisabled ? -1 : 0}
      role="button"
      aria-label="Upload image drag and drop area. Press Enter or Space to choose a file."
      onKeyDown={handleKeyDown}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={triggerFilePicker}
      className={`relative group border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all duration-300 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-950 ${
        isDragging
          ? 'border-blue-500 bg-blue-500/10 scale-[1.01] shadow-xl shadow-blue-500/10 ring-2 ring-blue-500/30'
          : 'border-slate-800 hover:border-blue-500/60 bg-slate-950/60 hover:bg-slate-900/60 shadow-inner'
      } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png, image/jpeg, image/jpg, image/webp"
        onChange={onFileSelect}
        disabled={isDisabled}
        className="hidden"
        aria-hidden="true"
      />

      {/* Decorative Icon Container */}
      <div
        className={`w-20 h-20 rounded-2xl flex items-center justify-center mb-5 transition-all duration-300 ${
          isDragging
            ? 'bg-blue-600/30 text-blue-400 scale-110 rotate-3'
            : 'bg-slate-900 border border-slate-800 text-blue-500 group-hover:scale-110 group-hover:border-blue-500/40 group-hover:bg-blue-500/10'
        }`}
      >
        {isDragging ? (
          <UploadCloud size={40} className="animate-bounce" />
        ) : (
          <ImageIcon size={38} className="transition-transform group-hover:scale-105" />
        )}
      </div>

      {/* Instruction Heading */}
      <h3 className="text-base font-semibold text-white mb-1.5 flex items-center gap-2">
        {isDragging ? (
          <span className="text-blue-400 font-bold">Drop your image here to upload</span>
        ) : (
          <span>Drag & Drop your image here</span>
        )}
      </h3>

      <p className="text-xs text-slate-400 max-w-sm mb-6 leading-relaxed">
        Upload a model avatar or garment photo for AI Virtual Fitting simulation.
      </p>

      {/* Browse Button */}
      <Button
        variant="primary"
        size="md"
        leftIcon={<UploadCloud size={16} />}
        isDisabled={isDisabled}
        onClick={(e) => {
          e.stopPropagation();
          triggerFilePicker();
        }}
        className="mb-6 pointer-events-auto"
      >
        Browse Files
      </Button>

      {/* Specifications & Constraints */}
      <div className="flex flex-wrap items-center justify-center gap-4 text-[11px] text-slate-400 pt-4 border-t border-slate-800/80 w-full max-w-md font-mono">
        <div className="flex items-center gap-1.5 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800">
          <FileText size={13} className="text-blue-400" />
          <span>Supported: PNG, JPG, JPEG, WEBP</span>
        </div>
        <div className="flex items-center gap-1.5 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800">
          <HardDrive size={13} className="text-purple-400" />
          <span>Max Size: 10 MB</span>
        </div>
      </div>
    </div>
  );
};
