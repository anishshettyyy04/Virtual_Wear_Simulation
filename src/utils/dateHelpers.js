/**
 * Formats ISO date string or timestamp into readable display format.
 * @param {string|number|Date} date
 * @returns {string}
 */
export const formatDate = (date = new Date()) => {
  const d = new Date(date);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
};
