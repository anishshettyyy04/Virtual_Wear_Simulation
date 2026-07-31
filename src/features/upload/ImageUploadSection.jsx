import { useImageUpload } from '@/hooks/useImageUpload';
import { UploadDropzone } from '@/components/upload/UploadDropzone';
import { ImagePreview } from '@/components/upload/ImagePreview';
import { UploadError } from '@/components/upload/UploadError';
import { UploadProgress } from '@/components/upload/UploadProgress';

/**
 * ImageUploadSection feature component that connects useImageUpload hook
 * with UploadDropzone, ImagePreview, UploadProgress, and UploadError components.
 */
export const ImageUploadSection = ({ onImageChange }) => {
  const {
    selectedImage,
    previewURL,
    fileName,
    fileSize,
    imageWidth,
    imageHeight,
    uploadTimestamp,
    uploadStatus,
    uploadError,
    uploadProgress,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileInputChange,
    removeImage,
    replaceImage,
    clearError,
  } = useImageUpload({ maxSizeMB: 10 });

  // Notify parent component if callback exists
  const handleRemove = () => {
    removeImage();
    if (onImageChange) onImageChange(null);
  };

  const handleReplace = (file) => {
    replaceImage(file);
    if (onImageChange) onImageChange(file);
  };

  return (
    <div className="space-y-6 w-full">
      {/* Upload Validation Error Banner */}
      {uploadError && (
        <UploadError
          error={uploadError}
          onDismiss={clearError}
        />
      )}

      {/* Conditional UI State Rendering */}
      {uploadStatus === 'uploading' && (
        <UploadProgress
          progress={uploadProgress}
          fileName={fileName}
          statusLabel="Uploading & Extracting Metadata..."
        />
      )}

      {selectedImage && (uploadStatus === 'uploaded' || uploadStatus === 'success') && (
        <ImagePreview
          previewURL={previewURL}
          fileName={fileName}
          fileSize={fileSize}
          imageWidth={imageWidth}
          imageHeight={imageHeight}
          uploadTimestamp={uploadTimestamp}
          onReplace={handleReplace}
          onRemove={handleRemove}
        />
      )}

      {uploadStatus !== 'uploading' && !selectedImage && (
        <UploadDropzone
          onFileSelect={handleFileInputChange}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          uploadStatus={uploadStatus}
        />
      )}
    </div>
  );
};
