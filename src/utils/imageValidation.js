import { APP_CONFIG } from '@/constants/appConfig';

/**
 * Validates file type against allowed mime types and extensions.
 * Allowed formats: PNG, JPG, JPEG, WEBP. Rejects all other formats.
 * @param {File} file
 * @returns {{ isValid: boolean, error?: string }}
 */
export const validateFileType = (file) => {
  if (!file) {
    return { isValid: false, error: 'No file provided.' };
  }

  const allowedTypes = APP_CONFIG.UPLOAD.ALLOWED_TYPES || ['image/jpeg', 'image/png', 'image/webp'];
  const fileType = file.type?.toLowerCase() || '';
  const fileName = file.name?.toLowerCase() || '';

  const isAllowedType = allowedTypes.includes(fileType);
  const isAllowedExt = /\.(png|jpe?g|webp)$/i.test(fileName);

  if (!isAllowedType && !isAllowedExt) {
    return {
      isValid: false,
      error: 'Unsupported file format. Please upload PNG, JPG, JPEG, or WEBP.',
    };
  }

  return { isValid: true };
};

/**
 * Validates file size against maximum megabyte threshold.
 * Default max size: 10 MB.
 * @param {File} file
 * @param {number} [maxMB=10]
 * @returns {{ isValid: boolean, error?: string }}
 */
export const validateFileSize = (file, maxMB = APP_CONFIG.UPLOAD.MAX_FILE_SIZE_MB || 10) => {
  if (!file) {
    return { isValid: false, error: 'No file provided.' };
  }

  const maxBytes = maxMB * 1024 * 1024;
  if (file.size > maxBytes) {
    return {
      isValid: false,
      error: `File exceeds ${maxMB}MB limit. (Current size: ${(file.size / (1024 * 1024)).toFixed(2)} MB)`,
    };
  }

  return { isValid: true };
};

/**
 * Formats file size in bytes to human-readable string (e.g. "2.4 MB", "450 KB").
 * @param {number} bytes
 * @returns {string}
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0 || !bytes || isNaN(bytes)) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Extracts width and height dimensions from an image File asynchronously.
 * @param {File} file
 * @returns {Promise<{ width: number | null, height: number | null }>}
 */
export const getImageDimensions = (file) => {
  return new Promise((resolve) => {
    if (!file || !file.type || !file.type.startsWith('image/')) {
      resolve({ width: null, height: null });
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
      const dimensions = {
        width: img.naturalWidth || img.width,
        height: img.naturalHeight || img.height,
      };
      URL.revokeObjectURL(objectUrl);
      resolve(dimensions);
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      resolve({ width: null, height: null });
    };

    img.src = objectUrl;
  });
};

/**
 * Comprehensive image validator combining file type and size checks.
 * @param {File} file
 * @param {number} [maxMB=10]
 * @returns {{ isValid: boolean, error?: string }}
 */
export const validateImageFile = (file, maxMB = 10) => {
  const typeValidation = validateFileType(file);
  if (!typeValidation.isValid) return typeValidation;

  const sizeValidation = validateFileSize(file, maxMB);
  if (!sizeValidation.isValid) return sizeValidation;

  return { isValid: true };
};
