import { useState, useCallback } from 'react';
import { validateImageFile } from '@/utils/imageValidation';
import { createImagePreviewUrl } from '@/utils/fileHelpers';

export const useImageUpload = (initialImage = null) => {
  const [imageState, setImageState] = useState(
    initialImage ? { file: null, previewUrl: initialImage, name: 'Default' } : null
  );
  const [error, setError] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const processFile = useCallback(async (file) => {
    setError(null);
    const validation = validateImageFile(file);
    if (!validation.isValid) {
      setError(validation.error);
      return false;
    }

    try {
      const previewUrl = await createImagePreviewUrl(file);
      setImageState({
        file,
        previewUrl,
        name: file.name,
        size: file.size,
        type: file.type,
      });
      return true;
    } catch (err) {
      setError('Failed to generate image preview.', err);
      return false;
    }
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const handleDrop = useCallback(
    async (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragActive(false);

      const files = e.dataTransfer?.files;
      if (files && files.length > 0) {
        await processFile(files[0]);
      }
    },
    [processFile]
  );

  const handleFileInputChange = useCallback(
    async (e) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        await processFile(files[0]);
      }
    },
    [processFile]
  );

  const clearImage = useCallback(() => {
    setImageState(null);
    setError(null);
  }, []);

  return {
    imageState,
    setImageState,
    error,
    setError,
    isDragActive,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileInputChange,
    processFile,
    clearImage,
  };
};
