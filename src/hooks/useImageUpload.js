import { useState, useCallback, useEffect, useRef } from 'react';
import {
  validateImageFile,
  formatFileSize,
  getImageDimensions,
} from '@/utils/imageValidation';

/**
 * Custom React hook for handling image file selection, validation,
 * local memory preview generation, fake upload simulation, and cleanup.
 *
 * @param {Object} [options]
 * @param {number} [options.maxSizeMB=10]
 * @returns {Object} Image upload state & handlers
 */
export const useImageUpload = (options = {}) => {
  const maxSizeMB = options.maxSizeMB || 10;

  const [selectedImage, setSelectedImage] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const [fileName, setFileName] = useState('');
  const [fileSize, setFileSize] = useState('');
  const [imageWidth, setImageWidth] = useState(null);
  const [imageHeight, setImageHeight] = useState(null);
  const [uploadTimestamp, setUploadTimestamp] = useState(null);
  
  // Status: 'idle' | 'dragging' | 'uploading' | 'uploaded' | 'error' | 'success'
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [uploadError, setUploadError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const activeUrlRef = useRef(null);
  const timeoutRef = useRef(null);
  const intervalRef = useRef(null);

  // Revoke object URL to avoid browser memory leaks
  const revokeCurrentPreview = useCallback(() => {
    if (activeUrlRef.current) {
      URL.revokeObjectURL(activeUrlRef.current);
      activeUrlRef.current = null;
    }
  }, []);

  // Cleanup timers and object URLs on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);
      revokeCurrentPreview();
    };
  }, [revokeCurrentPreview]);

  /**
   * Core function to validate and process an incoming File object.
   */
  const processFile = useCallback(
    async (file) => {
      // Reset current errors and set progress
      setUploadError(null);

      if (!file) {
        setUploadStatus('error');
        setUploadError('No file selected.');
        return false;
      }

      // Step 1: Validate file format & size
      const validation = validateImageFile(file, maxSizeMB);
      if (!validation.isValid) {
        setUploadStatus('error');
        setUploadError(validation.error);
        return false;
      }

      // Step 2: Start fake upload animation
      setUploadStatus('uploading');
      setUploadProgress(10);

      // Clear any running timers
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);

      // Generate preview object URL & dimensions asynchronously
      revokeCurrentPreview();
      const objectUrl = URL.createObjectURL(file);
      activeUrlRef.current = objectUrl;

      const dimensions = await getImageDimensions(file);

      // Simulate fake upload progress over 800 - 1200 ms
      const duration = Math.floor(Math.random() * 400) + 800; // 800ms to 1200ms
      const intervalTime = 50;
      const totalSteps = duration / intervalTime;
      let currentStep = 0;

      intervalRef.current = setInterval(() => {
        currentStep += 1;
        const progressPercent = Math.min(Math.round((currentStep / totalSteps) * 100), 95);
        setUploadProgress(progressPercent);
      }, intervalTime);

      return new Promise((resolve) => {
        timeoutRef.current = setTimeout(() => {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setUploadProgress(100);

          // Update state with selected image details
          setSelectedImage(file);
          setPreviewURL(objectUrl);
          setFileName(file.name);
          setFileSize(formatFileSize(file.size));
          setImageWidth(dimensions.width);
          setImageHeight(dimensions.height);

          const now = new Date();
          const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          setUploadTimestamp(`Today at ${timeStr}`);

          setUploadStatus('uploaded');
          resolve(true);
        }, duration);
      });
    },
    [maxSizeMB, revokeCurrentPreview]
  );

  /**
   * Drag Event Handlers
   */
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setUploadStatus((prev) => (prev !== 'uploading' ? 'dragging' : prev));
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setUploadStatus((prev) => (prev === 'dragging' ? 'idle' : prev));
  }, []);

  const handleDrop = useCallback(
    async (e) => {
      e.preventDefault();
      e.stopPropagation();
      setUploadStatus('idle');

      const files = e.dataTransfer?.files;
      if (files && files.length > 0) {
        await processFile(files[0]);
      }
    },
    [processFile]
  );

  /**
   * File Input Change Handler
   */
  const handleFileInputChange = useCallback(
    async (e) => {
      const files = e.target?.files;
      if (files && files.length > 0) {
        await processFile(files[0]);
      }
    },
    [processFile]
  );

  /**
   * Removes current image and resets state back to default placeholder dropzone.
   */
  const removeImage = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (intervalRef.current) clearInterval(intervalRef.current);

    revokeCurrentPreview();

    setSelectedImage(null);
    setPreviewURL(null);
    setFileName('');
    setFileSize('');
    setImageWidth(null);
    setImageHeight(null);
    setUploadTimestamp(null);
    setUploadStatus('idle');
    setUploadError(null);
    setUploadProgress(0);
  }, [revokeCurrentPreview]);

  /**
   * Replaces current image with a new File.
   */
  const replaceImage = useCallback(
    async (file) => {
      if (file) {
        await processFile(file);
      }
    },
    [processFile]
  );

  /**
   * Clears any active error state without removing uploaded image (if any).
   */
  const clearError = useCallback(() => {
    setUploadError(null);
    if (uploadStatus === 'error') {
      setUploadStatus(selectedImage ? 'uploaded' : 'idle');
    }
  }, [uploadStatus, selectedImage]);

  return {
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
    // Handlers
    processFile,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileInputChange,
    removeImage,
    replaceImage,
    clearError,
  };
};
