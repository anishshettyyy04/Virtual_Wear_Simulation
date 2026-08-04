/**
 * Helper utility to parse and format API errors into user-friendly messages.
 * @param {Error|object} error - Axios error or generic Error object
 * @returns {object} Standardized error object { message, code, status, details }
 */
export const parseApiError = (error) => {
  if (!error) {
    return {
      message: 'An unknown error occurred.',
      code: 'UNKNOWN_ERROR',
      status: 500,
    };
  }

  // Handle Axios response errors (HTTP 4xx / 5xx)
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;
    const rawError = data?.error;

    // Safely extract string message from response data or nested error object
    const message =
      (typeof data?.message === 'string' && data.message ? data.message : null) ||
      (typeof rawError === 'string'
        ? rawError
        : typeof rawError === 'object' && typeof rawError?.message === 'string'
          ? rawError.message
          : null) ||
      (status === 404
        ? 'Requested endpoint or resource not found.'
        : status === 401
          ? 'Unauthorized access. Please log in.'
          : status === 403
            ? 'Access forbidden.'
            : status === 422
              ? 'Invalid payload data provided.'
              : status >= 500
                ? 'Internal server error occurred on the AI backend.'
                : 'Request failed with status code ' + status);

    const code =
      (typeof rawError === 'object' && rawError?.code ? rawError.code : data?.code) ||
      `HTTP_${status}`;

    const requestId =
      (typeof rawError === 'object' && rawError?.request_id ? rawError.request_id : data?.request_id) || null;

    return {
      message: String(message),
      code,
      status,
      requestId,
      details: data?.details || (typeof rawError === 'object' ? rawError?.details : null) || null,
    };
  }

  // Handle network connectivity / request errors
  if (error.request) {
    return {
      message: 'Unable to reach backend server. Please check network connection or backend service status.',
      code: 'NETWORK_ERROR',
      status: 0,
    };
  }

  // Handle custom thrown errors
  return {
    message: error.message || 'An unexpected client error occurred.',
    code: error.code || 'CLIENT_ERROR',
    status: 400,
  };
};
