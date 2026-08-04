import axios from 'axios';
import { parseApiError } from '@/utils/apiErrorParser';

const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000/api/v1';
const timeout = Number(import.meta.env.VITE_API_TIMEOUT) || 120000;

export const api = axios.create({
  baseURL,
  timeout,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request Interceptor: attach authorization tokens dynamically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: parse backend error payloads & handle 401 unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const parsedError = parseApiError(error);

    // Handle 401 Unauthorized globally without causing infinite loops
    if (parsedError.status === 401 && typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    }

    return Promise.reject(parsedError);
  }
);

export default api;

