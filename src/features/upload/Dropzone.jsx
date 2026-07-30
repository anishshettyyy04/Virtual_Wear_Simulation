import { useRef } from 'react';
import { UploadCloud, Image as ImageIcon } from 'lucide-react';
import { useImageUpload } from '@/hooks/useImageUpload';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { validateImageFile } from '@/utils/imageValidation';
import { createImagePreviewUrl } from '@/utils/fileHelpers';

export const Dropzone = ({
  label = 'Upload Image',
  subtitle = 'Drag & drop image file or click to browse',
  onImageSelected,
}) => {
  const fileInputRef = useRef(null);
  const {
    error,
    isDragActive,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileInputChange,
  } = useImageUpload();

  const onInputChange = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      const validation = validateImageFile(file);
      if (validation.isValid) {
        const previewUrl = await createImagePreviewUrl(file);
        if (onImageSelected) {
          onImageSelected({ file, previewUrl, name: file.name, size: file.size });
        }
      }
    }
    await handleFileInputChange(e);
  };

  const onDropFile = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      const validation = validateImageFile(file);
      if (validation.isValid) {
        const previewUrl = await createImagePreviewUrl(file);
        if (onImageSelected) {
          onImageSelected({ file, previewUrl, name: file.name, size: file.size });
        }
      }
    }
    handleDrop(e);
  };

  return (
    <div className="w-full flex flex-col gap-2">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={onDropFile}
        onClick={() => fileInputRef.current?.click()}
        className={`relative w-full rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[220px] ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-500/10 shadow-lg shadow-indigo-500/10'
            : 'border-slate-800 hover:border-indigo-500/50 bg-slate-900/40 hover:bg-slate-900/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={onInputChange}
        />

        <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mb-3">
          {isDragActive ? (
            <UploadCloud size={28} className="animate-bounce" />
          ) : (
            <ImageIcon size={28} />
          )}
        </div>

        <h4 className="text-sm font-bold text-white mb-1">{label}</h4>
        <p className="text-xs text-slate-400 max-w-xs">{subtitle}</p>
        <span className="mt-3 text-[10px] text-slate-500 uppercase tracking-widest font-mono">
          JPG, PNG, WEBP (Max 10MB)
        </span>
      </div>

      {error && <ErrorMessage title="Upload Validation Error" message={error} />}
    </div>
  );
};
