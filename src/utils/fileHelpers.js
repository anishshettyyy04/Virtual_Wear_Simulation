/**
 * Converts a file object into a Data URL image preview string.
 * @param {File} file
 * @returns {Promise<string>}
 */
export const createImagePreviewUrl = (file) => {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('No file provided for preview generation.'));
      return;
    }

    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = (err) => reject(err);
    reader.readAsDataURL(file);
  });
};

/**
 * Formats bytes into human readable format (KB, MB).
 * @param {number} bytes
 * @returns {string}
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
