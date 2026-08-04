export const API_ENDPOINTS = {
  HEALTH: '/health',
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
    LOGOUT: '/auth/logout',
  },
  SIMULATION: {
    PROCESS: '/recommendations',
    TRYON: '/tryon',
    STATUS: '/simulation/status',
    CANCEL: '/simulation/cancel',
    HISTORY: '/simulation/history',
  },
  GARMENTS: {
    LIST: '/products',
    CATEGORIES: '/products/categories',
    UPLOAD: '/products/upload',
  },
  AI_MODEL: {
    STATUS: '/health',
    PRELOAD: '/ai/preload',
  },
};

