export const API_ENDPOINTS = {
  HEALTH: '/health',
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
    LOGOUT: '/auth/logout',
  },
  SIMULATION: {
    PROCESS: '/simulation/process',
    STATUS: '/simulation/status',
    CANCEL: '/simulation/cancel',
    HISTORY: '/simulation/history',
  },
  GARMENTS: {
    LIST: '/garments',
    CATEGORIES: '/garments/categories',
    UPLOAD: '/garments/upload',
  },
  AI_MODEL: {
    STATUS: '/ai/status',
    PRELOAD: '/ai/preload',
  },
};

