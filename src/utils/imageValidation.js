import { APP_CONFIG } from '@/constants/appConfig';

/**
 * Validates selected file against type and size boundaries.
 * @param {File} file
 * @returns {{ isValid: boolean, error?: string }}
 */
export const validateImageFile = (file) => {
  if (!file) {
    return { isValid: false, error: 'No file selected.' };
  }

  const { ALLOWED_TYPES, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB } = APP_CONFIG.UPLOAD;

  if (!ALLOWED_TYPES.includes(file.type)) {
    return {
      isValid: false,
      error: `Invalid file type "${file.type || 'unknown'}". Supported formats: JPG, PNG, WEBP.`,
    };
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    const sizeInMb = (file.size / (1024 * 1024)).toFixed(2);
    return {
      isValid: false,
      error: `File size (${sizeInMb} MB) exceeds maximum allowed size of ${MAX_FILE_SIZE_MB} MB.`,
    };
  }

  return { isValid: true };
};
